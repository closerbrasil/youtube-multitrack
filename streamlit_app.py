#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import subprocess
import json
import os
import re
import tempfile
from pathlib import Path
import shutil
import uuid
import io

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

# Função para identificar os melhores formatos de vídeo e áudio em pt-BR
def encontrar_formatos(url):
    try:
        # Obter informações detalhadas do vídeo
        resultado = subprocess.run(
            ["yt-dlp", "-j", url], 
            capture_output=True, 
            text=True
        )
        
        if resultado.returncode != 0:
            return None, None, None
        
        info = json.loads(resultado.stdout)
        titulo = info.get('title', 'Video')
        formatos = info.get('formats', [])
        
        # Procurar por áudios em português
        audios_pt = []
        for formato in formatos:
            # Verificar se é um formato de áudio
            if formato.get('vcodec') == 'none' and formato.get('acodec') != 'none':
                idioma = str(formato.get('language', '')).lower()
                
                # Verificar se é português
                if any(termo in idioma for termo in ['pt', 'br', 'portuguese']):
                    audios_pt.append(formato)
        
        # Encontrar melhor formato de vídeo até 1080p
        videos_hd = []
        for formato in formatos:
            # Verificar se é formato de vídeo sem áudio
            if formato.get('acodec') == 'none' and formato.get('vcodec') != 'none':
                altura = formato.get('height', 0)
                if isinstance(altura, int) and altura <= 1080 and altura >= 720:
                    videos_hd.append(formato)
        
        # Se encontrou formatos, ordenar por qualidade
        melhor_audio_pt = None
        if audios_pt:
            # Ordenar por bitrate/qualidade
            audios_pt.sort(key=lambda x: float(x.get('abr', 0) or 0), reverse=True)
            melhor_audio_pt = audios_pt[0]
            st.success(f"Áudio em português encontrado! ({melhor_audio_pt.get('format_id')})")
        
        melhor_video = None
        if videos_hd:
            # Ordenar por altura (resolução)
            videos_hd.sort(key=lambda x: x.get('height', 0), reverse=True)
            melhor_video = videos_hd[0]
            st.success(f"Vídeo em alta definição encontrado: {melhor_video.get('height')}p")
        
        return melhor_video, melhor_audio_pt, titulo
    
    except Exception as e:
        st.error(f"Erro ao processar o vídeo: {str(e)}")
        return None, None, None

# Método para baixar o vídeo e retornar os bytes
def baixar_video_direto(url, formato=None):
    try:
        # Criar um ID único para este download
        download_id = str(uuid.uuid4())
        
        # Criar diretório temporário no /tmp do sistema
        diretorio_temp = os.path.join("/tmp", download_id)
        os.makedirs(diretorio_temp, exist_ok=True)
        
        # Arquivo temporário para o download
        arquivo_temp = os.path.join(diretorio_temp, "video.mp4")
        
        # Preparar o comando
        comando = ["yt-dlp", "--merge-output-format", "mp4"]
        
        # Adicionar formato se especificado
        if formato:
            comando.extend(["-f", formato])
        else:
            comando.extend(["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]"])
        
        # Adicionar o caminho de saída e a URL
        comando.extend(["-o", arquivo_temp, url])
        
        # Executar o download (sem capturar stdout para permitir progresso)
        processo = subprocess.run(comando, check=True)
        
        # Verificar se o arquivo existe
        if os.path.exists(arquivo_temp):
            # Ler o arquivo em memória
            with open(arquivo_temp, "rb") as f:
                conteudo = f.read()
            
            # Limpar o diretório temporário
            shutil.rmtree(diretorio_temp, ignore_errors=True)
            
            return conteudo
        else:
            st.error(f"Arquivo não encontrado após download: {arquivo_temp}")
            return None
    except subprocess.CalledProcessError as e:
        st.error(f"Erro ao baixar vídeo: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return None

# Quando o usuário colar a URL
if url_video:
    # Verificar se é uma URL válida do YouTube
    if "youtube.com" not in url_video and "youtu.be" not in url_video:
        st.error("Por favor, insira uma URL válida do YouTube.")
    else:
        # Botão para iniciar o download
        if st.button("Baixar Vídeo", type="primary"):
            # Etapa 1: Analisar os formatos disponíveis
            with st.spinner("Analisando formatos disponíveis..."):
                video, audio_pt, titulo = encontrar_formatos(url_video)
                
                if not titulo:
                    st.error("Não foi possível processar o vídeo. Tente novamente.")
                else:
                    # Nome seguro para o arquivo
                    nome_seguro = re.sub(r'[^\w\-\. ]', '_', titulo)
                    nome_arquivo = f"{nome_seguro}.mp4"
                    
                    # Definir o formato para download
                    formato_download = None
                    if video and audio_pt:
                        formato_download = f"{video['format_id']}+{audio_pt['format_id']}"
                        st.info(f"Baixando vídeo {video.get('height', '')}p com áudio em português")
                    else:
                        st.info("Usando configuração padrão para o download")
                    
                    # Etapa 2: Baixar o vídeo
                    with st.spinner(f"Baixando '{titulo}'..."):
                        # Mostrar barra de progresso indeterminada
                        progress_bar = st.progress(0)
                        
                        # Tentar o download direto
                        video_bytes = baixar_video_direto(url_video, formato_download)
                        
                        if video_bytes:
                            # Download concluído
                            progress_bar.progress(1.0)
                            st.success("Download concluído!")
                            
                            # Mostrar o tamanho do arquivo
                            tamanho_mb = len(video_bytes) / (1024 * 1024)
                            st.info(f"Tamanho do arquivo: {tamanho_mb:.1f} MB")
                            
                            # Oferecer o botão de download
                            st.download_button(
                                label=f"💾 Salvar '{nome_arquivo}'",
                                data=video_bytes,
                                file_name=nome_arquivo,
                                mime="video/mp4"
                            )
                        else:
                            st.error("Não foi possível baixar o vídeo. Tente novamente.")
                            
                            # Tentar método alternativo mais simples
                            st.warning("Tentando método alternativo...")
                            try:
                                with st.spinner("Último método de tentativa..."):
                                    # Usar o formato mais simples possível
                                    video_bytes_alt = baixar_video_direto(url_video, "best")
                                    
                                    if video_bytes_alt:
                                        st.success("Download concluído com método alternativo!")
                                        
                                        # Oferecer para download
                                        st.download_button(
                                            label=f"💾 Salvar '{nome_arquivo}'",
                                            data=video_bytes_alt,
                                            file_name=nome_arquivo,
                                            mime="video/mp4"
                                        )
                            except Exception as e:
                                st.error(f"Todos os métodos de download falharam: {e}")

# Adicionar informações no rodapé
st.markdown("---")
st.markdown("**Nota:** Esta aplicação baixa vídeos do YouTube com a melhor qualidade até 1080p e seleciona automaticamente o áudio em português, quando disponível.")
st.markdown("Desenvolvido com ❤️ usando Streamlit e yt-dlp.") 