@echo off
SETLOCAL EnableDelayedExpansion

echo ==========================================
echo   Configuracao Automatica do Dashboard
echo ==========================================
echo.

:: 1. Verificar se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale o Python:
    echo 1. Acesse https://www.python.org/downloads/
    echo 2. Baixe o instalador para Windows.
    echo 3. IMPORTANTE: Marque a opcao "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado.
echo.

:: 2. Verificar/Criar Ambiente Virtual (venv)
if not exist "venv" (
    echo [INFO] Criando ambiente virtual 'venv'...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado.
) else (
    echo [INFO] Usando ambiente virtual existente.
)

:: 3. Ativar Ambiente Virtual
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERRO] Nao foi possivel ativar o ambiente virtual.
    pause
    exit /b 1
)

:: 4. Instalar Dependencias
echo [INFO] Verificando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao com a internet.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

:: 5. Executar o Dashboard
echo ==========================================
echo   Iniciando Dashboard...
echo ==========================================
streamlit run app.py

pause
