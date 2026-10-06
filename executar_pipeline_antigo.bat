@echo off
setlocal

REM ============================================================
REM Tesouro Direto Analytics - Execucao diaria do pipeline
REM ============================================================

set "PROJETO=C:\Users\lecan\OneDrive\Área de Trabalho\estudos_python\robo_tesouro\robo_tesouro_data_analytics_v2"
set "PYTHON=%PROJETO%\.venv\Scripts\python.exe"
set "LOG=%PROJETO%\outputs\pipeline.log"

if not exist "%PROJETO%" (
    echo ERRO: Pasta do projeto nao encontrada:
    echo %PROJETO%
    exit /b 1
)

if not exist "%PYTHON%" (
    echo ERRO: Python do ambiente virtual nao encontrado:
    echo %PYTHON%
    exit /b 1
)

if not exist "%PROJETO%\outputs" mkdir "%PROJETO%\outputs"

cd /d "%PROJETO%"

echo ============================================================ >> "%LOG%"
echo Inicio: %date% %time% >> "%LOG%"
echo ============================================================ >> "%LOG%"

"%PYTHON%" -m src.pipeline >> "%LOG%" 2>&1
set "CODIGO=%ERRORLEVEL%"

echo Fim: %date% %time% >> "%LOG%"
echo Codigo de retorno: %CODIGO% >> "%LOG%"
echo. >> "%LOG%"

if not "%CODIGO%"=="0" (
    echo ERRO: Pipeline terminou com codigo %CODIGO%.
    echo Consulte: %LOG%
) else (
    echo Pipeline executado com sucesso.
    echo Log: %LOG%
)

exit /b %CODIGO%
