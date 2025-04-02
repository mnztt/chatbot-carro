@echo off

:: Verificar se o Python está instalado
where python >nul 2>nul
if errorlevel 1 (
    echo Python não encontrado. Por favor, instale o Python 3.
    exit /b
)

:: Criar o ambiente virtual
python -m venv venv

:: Ativar o ambiente virtual
call venv\Scripts\activate.bat

:: Instalar as dependências do requirements.txt
pip install -r requirements.txt

:: Baixar os pacotes NLTK
python setup_nltk.py

echo Ambiente virtual criado, dependências instaladas e pacotes NLTK baixados.