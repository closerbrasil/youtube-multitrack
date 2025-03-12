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

# Quando o usuário colar a URL
if url_video:
    # Verificar se é uma URL válida do YouTube
    if "youtube.com" not in url_video and "youtu.be" not in url_video:
        st.error("Por favor, insira uma URL válida do YouTube.")
    else:
        # Botão para iniciar o download
        if st.button("Baixar Vídeo", type="primary"):
            with st.spinner("Analisando formatos disponíveis..."):
                video, audio_pt, titulo = encontrar_formatos(url_video)
                
                if not titulo:
                    st.error("Não foi possível processar o vídeo. Tente novamente.")
                else:
                    # Criar diretório temporário para o download
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Nome seguro para o arquivo
                        nome_seguro = re.sub(r'[^\w\-\. ]', '_', titulo)
                        caminho_arquivo = os.path.join(temp_dir, f"{nome_seguro}.mp4")
                        
                        try:
                            # Construir comando com base nos formatos disponíveis
                            comando_base = [
                                "yt-dlp",
                                "--merge-output-format", "mp4",
                                "-o", caminho_arquivo
                            ]
                            
                            # Se encontrou vídeo HD e áudio PT, usar esses formatos específicos
                            if video and audio_pt:
                                formato = f"{video['format_id']}+{audio_pt['format_id']}"
                                comando_base.extend(["-f", formato])
                                st.info(f"Baixando vídeo {video.get('height', '')}p com áudio em português")
                            else:
                                # Fallback: tenta os melhores formatos gerais
                                comando_base.extend(["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]"])
                                st.info("Áudio em português não disponível. Baixando com configuração padrão.")
                            
                            # Adicionar URL
                            comando_base.append(url_video)
                            
                            # Iniciar o download
                            with st.spinner(f"Baixando '{titulo}'..."):
                                processo = subprocess.Popen(
                                    comando_base,
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
                                    
                                    # Verificar se o arquivo foi criado
                                    arquivo_baixado = Path(caminho_arquivo)
                                    if arquivo_baixado.exists():
                                        # Mostrar tamanho do arquivo
                                        tamanho_mb = arquivo_baixado.stat().st_size / (1024 * 1024)
                                        st.info(f"Tamanho do arquivo: {tamanho_mb:.1f} MB")
                                        
                                        # Botão de download
                                        with open(arquivo_baixado, 'rb') as f:
                                            st.download_button(
                                                label=f"💾 Salvar '{nome_seguro}.mp4'",
                                                data=f,
                                                file_name=f"{nome_seguro}.mp4",
                                                mime="video/mp4"
                                            )
                                        
                                        st.info("Clique no botão acima para salvar o vídeo no seu dispositivo.")
                                    else:
                                        st.error("Arquivo não encontrado após o download.")
                                else:
                                    stderr = processo.stderr.read()
                                    st.error(f"Erro durante o download: {stderr}")
                                    
                                    # Tentar uma abordagem alternativa se falhar
                                    st.warning("Tentando método alternativo de download...")
                                    
                                    # Usar o formato "best" como fallback
                                    comando_alternativo = [
                                        "yt-dlp",
                                        "--merge-output-format", "mp4",
                                        "-f", "best",
                                        "-o", caminho_arquivo,
                                        url_video
                                    ]
                                    
                                    processo_alt = subprocess.run(comando_alternativo, capture_output=True, text=True)
                                    
                                    if processo_alt.returncode == 0:
                                        st.success("Download concluído com método alternativo!")
                                        
                                        if os.path.exists(caminho_arquivo):
                                            with open(caminho_arquivo, 'rb') as f:
                                                st.download_button(
                                                    label=f"💾 Salvar '{nome_seguro}.mp4'",
                                                    data=f,
                                                    file_name=f"{nome_seguro}.mp4",
                                                    mime="video/mp4"
                                                )
                                    else:
                                        st.error(f"Falha no método alternativo: {processo_alt.stderr}")
                        except Exception as e:
                            st.error(f"Erro ao baixar o vídeo: {str(e)}")

# Adicionar informações no rodapé
st.markdown("---")
st.markdown("**Nota:** Esta aplicação baixa vídeos do YouTube com a melhor qualidade até 1080p e seleciona automaticamente o áudio em português, quando disponível.")
st.markdown("Desenvolvido com ❤️ usando Streamlit e yt-dlp.") 