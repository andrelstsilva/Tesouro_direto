@echo off
chcp 65001 >nul
setlocal EnableExtensions

title Tesouro Direto Analytics - Pipeline Diario

REM ============================================================
REM O projeto deve conter este arquivo BAT na pasta raiz.
REM %~dp0 identifica automaticamente a pasta do BAT.
REM ============================================================

set "PROJETO=%~dp0"
set "PYTHON=%PROJETO%.venv\Scripts\python.exe"
set "OUTPUTS=%PROJETO%outputs"
set "LOG=%OUTPUTS%\pipeline.log"

echo ============================================================
echo       TESOURO DIRETO ANALYTICS
echo       EXECUCAO DO PIPELINE
echo ============================================================
echo.
echo Pasta do projeto:
echo %PROJETO%
echo.

REM ============================================================
REM Verifica a pasta do projeto
REM ============================================================

if not exist "%PROJETO%src\pipeline.py" (
    echo ERRO: src\pipeline.py nao foi encontrado.
    echo.
    echo Verifique se este BAT esta na pasta raiz do projeto.
    echo.
    pause
    exit /b 1
)

REM ============================================================
REM Verifica o Python do ambiente virtual
REM ============================================================

if not exist "%PYTHON%" (
    echo ERRO: Python do ambiente virtual nao foi encontrado.
    echo.
    echo Caminho esperado:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

REM ============================================================
REM Cria pasta de saida
REM ============================================================

if not exist "%OUTPUTS%" mkdir "%OUTPUTS%"

REM ============================================================
REM Entra na pasta do projeto
REM ============================================================

cd /d "%PROJETO%"

echo Python:
echo %PYTHON%
echo.

echo ============================================================
echo INICIANDO PIPELINE
echo ============================================================
echo.

echo ============================================================ >> "%LOG%"
echo INICIO: %date% %time% >> "%LOG%"
echo PROJETO: %PROJETO% >> "%LOG%"
echo ============================================================ >> "%LOG%"

"%PYTHON%" -m src.pipeline >> "%LOG%" 2>&1

set "CODIGO=%ERRORLEVEL%"

echo.
echo ============================================================
echo RESULTADO DA EXECUCAO
echo ============================================================
echo.

if "%CODIGO%"=="0" (
    echo SUCESSO!
    echo.
    echo O pipeline foi executado corretamente.
    echo O banco de dados foi atualizado.
) else (
    echo ERRO!
    echo.
    echo O pipeline terminou com codigo: %CODIGO%.
    echo.
    echo Consulte o arquivo:
    echo %LOG%
)

echo.
echo FIM: %date% %time% >> "%LOG%"
echo CODIGO DE RETORNO: %CODIGO% >> "%LOG%"
echo. >> "%LOG%"

echo Log:
echo %LOG%
echo.
echo ============================================================
echo Pressione qualquer tecla para fechar.
echo ============================================================

pause >nul

exit /b %CODIGO%
