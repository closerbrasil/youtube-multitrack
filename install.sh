#!/bin/bash

# Script de instalação para o YouTube Downloader com Seleção de Faixa de Áudio
# Este script instala as dependências necessárias para executar o aplicativo

echo "========================================================"
echo "Instalando dependências para o YouTube Downloader"
echo "========================================================"

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    echo "Erro: pip não está instalado. Por favor, instale o Python e o pip primeiro."
    exit 1
fi

# Verificar se o yt-dlp está instalado
if ! command -v yt-dlp &> /dev/null; then
    echo "Instalando yt-dlp..."
    pip install -U yt-dlp
else
    echo "yt-dlp já está instalado. Atualizando para a versão mais recente..."
    pip install -U yt-dlp
fi

# Instalar Streamlit
echo "Instalando Streamlit..."
pip install streamlit

# Verificar se é macOS e instalar yt-dlp via Homebrew se disponível
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        echo "Sistema macOS detectado. Verificando instalação via Homebrew..."
        if ! brew list yt-dlp &> /dev/null; then
            echo "Instalando yt-dlp via Homebrew para garantir a melhor compatibilidade..."
            brew install yt-dlp
        else
            echo "yt-dlp já está instalado via Homebrew. Atualizando..."
            brew upgrade yt-dlp
        fi
    fi
fi

# Criar diretório de downloads
if [ ! -d "downloads" ]; then
    echo "Criando diretório de downloads..."
    mkdir -p downloads
fi

# Tornar os scripts executáveis
echo "Tornando os scripts executáveis..."
chmod +x youtube_downloader.py youtube_downloader.js streamlit_app.py

echo "========================================================"
echo "Instalação concluída!"
echo ""
echo "Para executar a interface gráfica:"
echo "    streamlit run streamlit_app.py"
echo ""
echo "Para usar o script Python:"
echo "    ./youtube_downloader.py URL_DO_VIDEO"
echo ""
echo "Para usar o script JavaScript (requer Bun):"
echo "    ./youtube_downloader.js URL_DO_VIDEO"
echo "========================================================" 