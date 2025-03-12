# YouTube Downloader com Seleção de Faixa de Áudio

Este projeto contém scripts para baixar vídeos do YouTube com faixas de áudio específicas. Isso é útil quando um vídeo tem múltiplas faixas de áudio (diferentes idiomas, comentários, etc.) e você deseja escolher qual delas baixar.

## Pré-requisitos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) instalado no sistema
- Python 3.6+ (para os scripts Python)
- [Bun](https://bun.sh/) (para o script JavaScript)
- [Streamlit](https://streamlit.io/) (para a interface gráfica)

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Certifique-se de que o yt-dlp está instalado:
   ```bash
   # Instalar yt-dlp
   pip install -U yt-dlp
   # ou
   brew install yt-dlp  # no macOS com Homebrew
   ```
3. Se for usar o script JavaScript, instale o Bun:
   ```bash
   # macOS, Linux ou WSL
   curl -fsSL https://bun.sh/install | bash
   ```
4. Se for usar a interface gráfica, instale o Streamlit:
   ```bash
   pip install streamlit
   ```

## Como usar

### Interface gráfica com Streamlit (Recomendado)

A maneira mais fácil e amigável de usar este aplicativo é através da interface gráfica com Streamlit:

1. Execute o aplicativo Streamlit:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Seu navegador abrirá automaticamente com a interface do aplicativo.

3. Digite a URL do vídeo do YouTube que deseja baixar.

4. Escolha entre modo automático (recomendado) ou manual para selecionar a qualidade.

5. Se necessário, ajuste as configurações avançadas (idioma e resolução máxima).

6. Clique no botão "Baixar Vídeo" e aguarde o download ser concluído.

7. O vídeo será salvo na pasta "downloads".

### Usando o script Python

1. Torne o script executável:
   ```bash
   chmod +x youtube_downloader.py
   ```

2. Execute o script com a URL do vídeo:
   ```bash
   ./youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO"
   ```

3. O script mostrará todas as faixas de áudio e formatos de vídeo disponíveis
4. Escolha entre seleção automática ou manual:
   - **Automática (recomendada)**: O script escolherá a melhor qualidade de áudio no idioma preferido e a melhor qualidade de vídeo até a resolução máxima especificada
   - **Manual**: Você precisará digitar os IDs de áudio e vídeo manualmente

5. O vídeo será baixado na pasta `downloads`

### Usando o script JavaScript (com Bun)

1. Torne o script executável:
   ```bash
   chmod +x youtube_downloader.js
   ```

2. Execute o script com a URL do vídeo:
   ```bash
   ./youtube_downloader.js "https://www.youtube.com/watch?v=ID_DO_VIDEO"
   # ou
   bun youtube_downloader.js "https://www.youtube.com/watch?v=ID_DO_VIDEO"
   ```

3. O script mostrará todas as faixas de áudio e formatos de vídeo disponíveis
4. Escolha entre seleção automática ou manual:
   - **Automática (recomendada)**: O script escolherá a melhor qualidade de áudio no idioma preferido e a melhor qualidade de vídeo até a resolução máxima especificada
   - **Manual**: Você precisará digitar os IDs de áudio e vídeo manualmente

5. O vídeo será baixado na pasta `downloads`

### Seleção Automática

A seleção automática facilita o download sem precisar entender os termos técnicos:

1. Quando perguntado "Deseja escolher automaticamente a melhor qualidade?", pressione Enter ou digite "S"
2. Digite o idioma preferido (ou deixe em branco para português do Brasil)
3. Digite a resolução máxima desejada (ou deixe em branco para 1080p)
4. O script selecionará automaticamente:
   - A melhor faixa de áudio no idioma escolhido
   - O melhor formato de vídeo até a resolução especificada

### Usando o yt-dlp diretamente

Se preferir usar o yt-dlp diretamente, siga estes passos:

1. Liste todos os formatos disponíveis:
   ```bash
   yt-dlp -F "https://www.youtube.com/watch?v=ID_DO_VIDEO"
   ```

2. Identifique o ID da faixa de áudio desejada e o ID do formato de vídeo
   - As faixas de áudio são marcadas como "audio only"
   - Os formatos de vídeo (sem áudio) são marcados com "video only"

3. Baixe o vídeo com a faixa de áudio específica:
   ```bash
   yt-dlp -f VIDEO_ID+AUDIO_ID "https://www.youtube.com/watch?v=ID_DO_VIDEO"
   ```

   Por exemplo:
   ```bash
   yt-dlp -f 137+251 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   ```

## Exemplos de uso

### Baixar um vídeo com áudio em português usando a interface gráfica

1. Execute a interface gráfica: `streamlit run streamlit_app.py`
2. Cole a URL do vídeo do YouTube
3. Verifique se o idioma preferido está definido como "pt-BR"
4. Ajuste a resolução máxima se desejar
5. Clique em "Baixar Vídeo"

### Baixar um vídeo com áudio em português usando seleção automática no script

```bash
# 1. Execute o script
./youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO"

# 2. Quando perguntado, escolha a seleção automática (pressione Enter)
# 3. Deixe o idioma em branco para português do Brasil (pressione Enter)
# 4. Deixe a resolução em branco para 1080p (pressione Enter)
# 5. O vídeo será baixado automaticamente com a melhor qualidade disponível
```

### Baixar um vídeo com áudio em português manualmente

```bash
# 1. Listar formatos disponíveis
yt-dlp -F "https://www.youtube.com/watch?v=ID_DO_VIDEO"

# 2. Procurar pela faixa de áudio em português (geralmente indicada como [pt] ou [pt-BR])
# Suponha que o ID da faixa de áudio em português seja 251 e o formato de vídeo HD seja 137

# 3. Baixar o vídeo com áudio em português
yt-dlp -f 137+251 "https://www.youtube.com/watch?v=ID_DO_VIDEO"
```

## Capturas de tela

### Interface gráfica com Streamlit
![Interface gráfica](screenshots/streamlit_interface.png)

## Notas

- Os vídeos baixados serão salvos no formato MKV, que é capaz de conter diferentes codecs de vídeo e áudio
- Para baixar apenas o áudio, use `-f AUDIO_ID`
- Para baixar com a melhor qualidade de vídeo e áudio específico, use `-f best+AUDIO_ID`
- A seleção automática escolhe:
  - Áudio: Preferência para faixas de qualidade média no idioma escolhido, com preferência para o formato m4a
  - Vídeo: Maior resolução disponível até o limite especificado, com preferência para codecs mais eficientes (AV1)

## Licença

Este projeto é distribuído sob a licença MIT. 