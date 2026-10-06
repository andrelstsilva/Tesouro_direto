@echo off
setlocal
title Tesouro Direto Analytics - Pipeline Diario
set "PROJETO=C:\Users\lecan\OneDrive\Área de Trabalho\estudos_python\robo_tesouro\robo_tesouro_data_analytics_v2\"
set "PYTHON=%PROJETO%\.venv\Scripts\python.exe"
set "OUTPUTS=%PROJETO%\outputs"
set "LOG=%OUTPUTS%\pipeline.log"

echo ============================================================
echo       TESOURO DIRETO ANALYTICS
echo       EXECUCAO DO PIPELINE
echo ============================================================
echo.
echo Projeto:
echo %PROJETO%
echo.

if not exist "%PROJETO%" (
    echo ERRO: Pasta do projeto nao encontrada.
    echo %PROJETO%
    pause
    exit /b 1
)

if not exist "%PYTHON%" (
    echo ERRO: Python do ambiente virtual nao encontrado.
    echo %PYTHON%
    pause
    exit /b 1
)

if not exist "%OUTPUTS%" mkdir "%OUTPUTS%"
cd /d "%PROJETO%"

echo Python:
echo %PYTHON%
echo.
echo ============================================================
echo Iniciando pipeline...
echo ============================================================
echo.

echo ============================================================ >> "%LOG%"
echo INICIO: %date% %time% >> "%LOG%"
echo ============================================================ >> "%LOG%"

"%PYTHON%" -m src.pipeline
set "CODIGO=%ERRORLEVEL%"

 echo.
echo ============================================================
echo RESULTADO DA EXECUCAO
echo ============================================================
echo.

if "%CODIGO%"=="0" (
    echo SUCESSO!
    echo O pipeline foi executado corretamente.
    echo O banco de dados foi atualizado.
) else (
    echo ERRO! Codigo de retorno: %CODIGO%
    echo Consulte: %LOG%
)

echo FIM: %date% %time% >> "%LOG%"
echo CODIGO DE RETORNO: %CODIGO% >> "%LOG%"
echo. >> "%LOG%"

echo.
echo Log: %LOG%
echo.
pause
exit /b %CODIGO%
