#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import json
import os
import re

def obter_formatos(url):
    """Obtém todos os formatos disponíveis para o vídeo."""
    comando = ["yt-dlp", "-j", url]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print(f"Erro ao obter informações do vídeo: {resultado.stderr}")
        sys.exit(1)
    
    info = json.loads(resultado.stdout)
    return info.get("formats", []), info.get("title", "Video")

def mostrar_formatos_audio(formatos):
    """Mostra apenas os formatos de áudio disponíveis."""
    print("\nFaixas de áudio disponíveis:")
    print("ID\tExtensão\tCodec\t\tBitrate\tIdioma/Descrição")
    print("-" * 80)
    
    formatos_audio = []
    for formato in formatos:
        if formato.get("vcodec") == "none" or formato.get("acodec") != "none" and "audio only" in formato.get("format", ""):
            idioma = formato.get("language", "")
            if not idioma:
                idioma = "desconhecido"
            
            descricao = formato.get("format_note", "")
            
            print(f"{formato['format_id']}\t{formato.get('ext', 'N/A')}\t\t{formato.get('acodec', 'N/A')}\t\t{formato.get('abr', 'N/A')}k\t{idioma} {descricao}")
            formatos_audio.append(formato)
    
    return formatos_audio

def mostrar_formatos_video(formatos):
    """Mostra apenas os formatos de vídeo (sem áudio) disponíveis."""
    print("\nFormatos de vídeo disponíveis (sem áudio):")
    print("ID\tExtensão\tResolução\tCodec\t\tBitrate")
    print("-" * 80)
    
    formatos_video = []
    for formato in formatos:
        if formato.get("acodec") == "none" and formato.get("vcodec") != "none":
            print(f"{formato['format_id']}\t{formato.get('ext', 'N/A')}\t\t{formato.get('resolution', 'N/A')}\t\t{formato.get('vcodec', 'N/A')}\t\t{formato.get('vbr', 'N/A')}k")
            formatos_video.append(formato)
    
    return formatos_video

def encontrar_melhor_audio(formatos_audio, idioma_preferido="pt-BR"):
    """Encontra a melhor faixa de áudio no idioma preferido."""
    # Filtrar por idioma preferido
    audios_idioma = [f for f in formatos_audio if idioma_preferido.lower() in str(f.get("language", "")).lower()]
    
    # Se não encontrar no idioma preferido, use qualquer um
    if not audios_idioma:
        audios_idioma = formatos_audio
    
    # Procurar por áudios de qualidade média ou alta
    audios_medium = [f for f in audios_idioma if "medium" in str(f.get("format_note", "")).lower()]
    if audios_medium:
        # Preferir m4a sobre webm para compatibilidade
        for audio in audios_medium:
            if audio.get("ext") == "m4a":
                return audio["format_id"]
        # Se não encontrar m4a, use o primeiro de qualidade média
        return audios_medium[0]["format_id"]
    
    # Se não encontrar de qualidade média, use o de maior bitrate
    audios_idioma.sort(key=lambda x: float(x.get("abr", 0) or 0), reverse=True)
    if audios_idioma:
        return audios_idioma[0]["format_id"]
    
    # Se tudo falhar, retorne None
    return None

def encontrar_melhor_video(formatos_video, resolucao_maxima=1080):
    """Encontra o melhor formato de vídeo até a resolução máxima especificada."""
    # Filtrar por resolução máxima
    videos_filtrados = []
    for formato in formatos_video:
        resolucao = formato.get("resolution", "")
        if isinstance(resolucao, str) and "x" in resolucao:
            altura = int(resolucao.split("x")[1])
            if altura <= resolucao_maxima:
                videos_filtrados.append((formato, altura))
    
    # Ordenar por altura (resolução) em ordem decrescente
    videos_filtrados.sort(key=lambda x: x[1], reverse=True)
    
    if videos_filtrados:
        # Pegar o vídeo com maior resolução
        melhor_video = videos_filtrados[0][0]
        
        # Preferir codecs mais eficientes (AV1 > VP9 > H.264)
        for video, _ in videos_filtrados:
            if video["height"] == melhor_video["height"]:
                codec = video.get("vcodec", "").lower()
                if "av01" in codec:  # AV1
                    return video["format_id"]
        
        # Se não encontrar AV1, use o de maior resolução
        return melhor_video["format_id"]
    
    # Se tudo falhar, retorne None
    return None

def baixar_video(url, id_video, id_audio, pasta_destino="."):
    """Baixa o vídeo com a faixa de áudio especificada."""
    comando = [
        "yt-dlp", 
        "-f", f"{id_video}+{id_audio}", 
        "-o", f"{pasta_destino}/%(title)s.%(ext)s",
        url
    ]
    
    print(f"\nBaixando vídeo com formato de vídeo {id_video} e áudio {id_audio}...")
    subprocess.run(comando)

def main():
    if len(sys.argv) < 2:
        print("Uso: python youtube_downloader.py URL_DO_VIDEO")
        sys.exit(1)
    
    url = sys.argv[1]
    formatos, titulo = obter_formatos(url)
    
    print(f"Título do vídeo: {titulo}")
    
    formatos_audio = mostrar_formatos_audio(formatos)
    formatos_video = mostrar_formatos_video(formatos)
    
    if not formatos_audio:
        print("Nenhuma faixa de áudio encontrada.")
        sys.exit(1)
    
    if not formatos_video:
        print("Nenhum formato de vídeo encontrado.")
        sys.exit(1)
    
    # Opção automática ou manual
    escolha = input("\nDeseja escolher automaticamente a melhor qualidade? (S/n): ").strip().lower()
    
    if escolha == "" or escolha == "s":
        # Escolha automática
        idioma_preferido = input("Digite o idioma preferido (deixe em branco para português do Brasil): ").strip()
        if not idioma_preferido:
            idioma_preferido = "pt-BR"
        
        resolucao_maxima = input("Digite a resolução máxima desejada (deixe em branco para 1080p): ").strip()
        if not resolucao_maxima:
            resolucao_maxima = 1080
        else:
            try:
                resolucao_maxima = int(resolucao_maxima)
            except ValueError:
                print("Resolução inválida, usando 1080p como padrão.")
                resolucao_maxima = 1080
        
        id_audio = encontrar_melhor_audio(formatos_audio, idioma_preferido)
        id_video = encontrar_melhor_video(formatos_video, resolucao_maxima)
        
        if not id_audio:
            print("Não foi possível encontrar uma faixa de áudio adequada.")
            sys.exit(1)
        
        if not id_video:
            print("Não foi possível encontrar um formato de vídeo adequado.")
            sys.exit(1)
        
        print(f"\nSelecionado automaticamente:")
        print(f"- Áudio: {id_audio}")
        print(f"- Vídeo: {id_video}")
    else:
        # Escolha manual
        id_audio = input("\nDigite o ID da faixa de áudio desejada: ")
        id_video = input("Digite o ID do formato de vídeo desejado: ")
        
        # Verificar se os IDs existem
        audio_valido = any(f["format_id"] == id_audio for f in formatos_audio)
        video_valido = any(f["format_id"] == id_video for f in formatos_video)
        
        if not audio_valido:
            print(f"ID de áudio '{id_audio}' não encontrado.")
            sys.exit(1)
        
        if not video_valido:
            print(f"ID de vídeo '{id_video}' não encontrado.")
            sys.exit(1)
    
    # Criar pasta de destino se não existir
    pasta_destino = "downloads"
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Baixar o vídeo
    baixar_video(url, id_video, id_audio, pasta_destino)
    print(f"\nDownload concluído! O arquivo foi salvo na pasta '{pasta_destino}'.")

if __name__ == "__main__":
    main() 