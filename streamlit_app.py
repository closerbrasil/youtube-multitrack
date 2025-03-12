#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import subprocess
import json
import os
import re
import tempfile
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

# Título principal
st.title("YouTube Downloader 🎬")
st.write("Baixe vídeos do YouTube com áudio em português (quando disponível)")

# Campo para URL do vídeo
url_video = st.text_input("Cole aqui a URL do vídeo do YouTube", placeholder="https://www.youtube.com/watch?v=...")

# Função para obter o melhor formato de áudio em português
def obter_melhor_formato(url):
    try:
        # Obter informações do vídeo
        comando = ["yt-dlp", "-j", url]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        if resultado.returncode != 0:
            return None, None, None
        
        info = json.loads(resultado.stdout)
        formatos = info.get("formats", [])
        titulo = info.get("title", "Video")
        
        # Encontrar melhor formato de vídeo (1080p ou menor)
        melhor_video = None
        for formato in formatos:
            if formato.get("acodec") == "none" and formato.get("vcodec") != "none":
                resolucao = formato.get("resolution", "")
                if isinstance(resolucao, str) and "x" in resolucao:
                    altura = int(resolucao.split("x")[1])
                    if altura <= 1080:
                        if melhor_video is None or altura > int(melhor_video.get("resolution", "0x0").split("x")[1]):
                            melhor_video = formato
        
        # Encontrar melhor formato de áudio em português
        melhor_audio = None
        for formato in formatos:
            if formato.get("vcodec") == "none" and formato.get("acodec") != "none":
                idioma = str(formato.get("language", "")).lower()
                if "pt" in idioma or "br" in idioma:
                    if melhor_audio is None or formato.get("abr", 0) > melhor_audio.get("abr", 0):
                        melhor_audio = formato
        
        # Se não encontrar áudio em português, usar o melhor áudio disponível
        if not melhor_audio:
            for formato in formatos:
                if formato.get("vcodec") == "none" and formato.get("acodec") != "none":
                    if melhor_audio is None or formato.get("abr", 0) > melhor_audio.get("abr", 0):
                        melhor_audio = formato
        
        return melhor_video, melhor_audio, titulo
    except Exception as e:
        st.error(f"Erro ao processar o vídeo: {str(e)}")
        return None, None, None

# Quando o usuário colar a URL
if url_video:
    # Verificar se é uma URL válida do YouTube
    if "youtube.com" not in url_video and "youtu.be" not in url_video:
        st.error("Por favor, insira uma URL válida do YouTube.")
    else:
        # Botão para iniciar o download
        if st.button("Baixar Vídeo", type="primary"):
            with st.spinner("Processando o vídeo..."):
                video, audio, titulo = obter_melhor_formato(url_video)
                
                if not video or not audio:
                    st.error("Não foi possível processar o vídeo. Tente novamente.")
                else:
                    # Criar diretório temporário para o download
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Nome seguro para o arquivo
                        nome_seguro = re.sub(r'[^\w\-\. ]', '_', titulo)
                        caminho_arquivo = os.path.join(temp_dir, f"{nome_seguro}.%(ext)s")
                        
                        # Iniciar o download
                        comando = [
                            "yt-dlp",
                            "-f", f"{video['format_id']}+{audio['format_id']}",
                            "-o", caminho_arquivo,
                            url_video
                        ]
                        
                        processo = subprocess.Popen(
                            comando,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                            universal_newlines=True
                        )
                        
                        # Mostrar progresso
                        barra_progresso = st.progress(0)
                        status = st.empty()
                        
                        # Ler saída e atualizar progresso
                        for linha in processo.stdout:
                            if "%" in linha:
                                match = re.search(r'(\d+\.\d+)%', linha)
                                if match:
                                    porcentagem = float(match.group(1))
                                    barra_progresso.progress(porcentagem / 100)
                            status.text(linha.strip())
                        
                        # Verificar resultado
                        if processo.wait() == 0:
                            barra_progresso.progress(1.0)
                            st.success("Download concluído!")
                            
                            # Encontrar o arquivo baixado
                            arquivos = list(Path(temp_dir).glob("*.*"))
                            if arquivos:
                                arquivo_baixado = arquivos[0]
                                
                                # Ler o arquivo para download pelo usuário
                                with open(arquivo_baixado, 'rb') as f:
                                    st.download_button(
                                        label=f"💾 Salvar '{nome_seguro}'",
                                        data=f,
                                        file_name=os.path.basename(arquivo_baixado),
                                        mime="video/mp4"
                                    )
                                
                                st.info("Clique no botão acima para salvar o vídeo no seu dispositivo.")
                            else:
                                st.error("Arquivo não encontrado após o download.")
                        else:
                            stderr = processo.stderr.read()
                            st.error(f"Erro durante o download: {stderr}")

# Adicionar informações no rodapé
st.markdown("---")
st.markdown("**Nota:** Esta aplicação baixa vídeos do YouTube com a melhor qualidade até 1080p e seleciona automaticamente o áudio em português, quando disponível.")
st.markdown("Desenvolvido com ❤️ usando Streamlit e yt-dlp.") 