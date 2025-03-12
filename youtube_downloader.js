#!/usr/bin/env bun

/**
 * Script para baixar vídeos do YouTube com faixas de áudio específicas
 * Requer: bun e yt-dlp instalados
 */

import { spawn } from 'child_process';
import { mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';
import readline from 'readline';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Função para executar comandos e retornar a saída
async function executarComando(comando, args) {
  return new Promise((resolve, reject) => {
    const processo = spawn(comando, args);
    let saida = '';
    let erro = '';

    processo.stdout.on('data', (dados) => {
      saida += dados.toString();
    });

    processo.stderr.on('data', (dados) => {
      erro += dados.toString();
    });

    processo.on('close', (codigo) => {
      if (codigo !== 0) {
        reject(new Error(`Comando falhou com código ${codigo}: ${erro}`));
      } else {
        resolve(saida);
      }
    });
  });
}

// Função para perguntar ao usuário
function perguntar(pergunta) {
  return new Promise((resolve) => {
    rl.question(pergunta, (resposta) => {
      resolve(resposta);
    });
  });
}

// Função para obter informações do vídeo
async function obterInfoVideo(url) {
  try {
    const saida = await executarComando('yt-dlp', ['-j', url]);
    return JSON.parse(saida);
  } catch (erro) {
    console.error('Erro ao obter informações do vídeo:', erro.message);
    process.exit(1);
  }
}

// Função para mostrar formatos de áudio disponíveis
function mostrarFormatosAudio(formatos) {
  console.log('\nFaixas de áudio disponíveis:');
  console.log('ID\tExtensão\tCodec\t\tBitrate\tIdioma/Descrição');
  console.log('-'.repeat(80));

  const formatosAudio = formatos.filter(formato => 
    formato.vcodec === 'none' || 
    (formato.acodec !== 'none' && formato.format && formato.format.includes('audio only'))
  );

  formatosAudio.forEach(formato => {
    const idioma = formato.language || 'desconhecido';
    const descricao = formato.format_note || '';
    console.log(`${formato.format_id}\t${formato.ext || 'N/A'}\t\t${formato.acodec || 'N/A'}\t\t${formato.abr || 'N/A'}k\t${idioma} ${descricao}`);
  });

  return formatosAudio;
}

// Função para mostrar formatos de vídeo disponíveis
function mostrarFormatosVideo(formatos) {
  console.log('\nFormatos de vídeo disponíveis (sem áudio):');
  console.log('ID\tExtensão\tResolução\tCodec\t\tBitrate');
  console.log('-'.repeat(80));

  const formatosVideo = formatos.filter(formato => 
    formato.acodec === 'none' && formato.vcodec !== 'none'
  );

  formatosVideo.forEach(formato => {
    console.log(`${formato.format_id}\t${formato.ext || 'N/A'}\t\t${formato.resolution || 'N/A'}\t\t${formato.vcodec || 'N/A'}\t\t${formato.vbr || 'N/A'}k`);
  });

  return formatosVideo;
}

// Função para encontrar a melhor faixa de áudio no idioma preferido
function encontrarMelhorAudio(formatosAudio, idiomaPreferido = 'pt-BR') {
  // Filtrar por idioma preferido
  let audiosIdioma = formatosAudio.filter(formato => 
    formato.language && formato.language.toLowerCase().includes(idiomaPreferido.toLowerCase())
  );
  
  // Se não encontrar no idioma preferido, use qualquer um
  if (audiosIdioma.length === 0) {
    audiosIdioma = formatosAudio;
  }
  
  // Procurar por áudios de qualidade média ou alta
  const audiosMedium = audiosIdioma.filter(formato => 
    formato.format_note && formato.format_note.toLowerCase().includes('medium')
  );
  
  if (audiosMedium.length > 0) {
    // Preferir m4a sobre webm para compatibilidade
    const m4aAudio = audiosMedium.find(audio => audio.ext === 'm4a');
    if (m4aAudio) {
      return m4aAudio.format_id;
    }
    // Se não encontrar m4a, use o primeiro de qualidade média
    return audiosMedium[0].format_id;
  }
  
  // Se não encontrar de qualidade média, use o de maior bitrate
  audiosIdioma.sort((a, b) => (b.abr || 0) - (a.abr || 0));
  if (audiosIdioma.length > 0) {
    return audiosIdioma[0].format_id;
  }
  
  // Se tudo falhar, retorne null
  return null;
}

// Função para encontrar o melhor formato de vídeo
function encontrarMelhorVideo(formatosVideo, resolucaoMaxima = 1080) {
  // Filtrar por resolução máxima
  const videosFiltrados = [];
  
  for (const formato of formatosVideo) {
    const resolucao = formato.resolution;
    if (typeof resolucao === 'string' && resolucao.includes('x')) {
      const altura = parseInt(resolucao.split('x')[1]);
      if (altura <= resolucaoMaxima) {
        videosFiltrados.push([formato, altura]);
      }
    }
  }
  
  // Ordenar por altura (resolução) em ordem decrescente
  videosFiltrados.sort((a, b) => b[1] - a[1]);
  
  if (videosFiltrados.length > 0) {
    // Pegar o vídeo com maior resolução
    const melhorVideo = videosFiltrados[0][0];
    
    // Preferir codecs mais eficientes (AV1 > VP9 > H.264)
    for (const [video, _] of videosFiltrados) {
      if (video.height === melhorVideo.height) {
        const codec = (video.vcodec || '').toLowerCase();
        if (codec.includes('av01')) {  // AV1
          return video.format_id;
        }
      }
    }
    
    // Se não encontrar AV1, use o de maior resolução
    return melhorVideo.format_id;
  }
  
  // Se tudo falhar, retorne null
  return null;
}

// Função para baixar o vídeo
async function baixarVideo(url, idVideo, idAudio, pastaDestino) {
  console.log(`\nBaixando vídeo com formato de vídeo ${idVideo} e áudio ${idAudio}...`);
  
  try {
    await executarComando('yt-dlp', [
      '-f', `${idVideo}+${idAudio}`,
      '-o', `${pastaDestino}/%(title)s.%(ext)s`,
      url
    ]);
    console.log(`\nDownload concluído! O arquivo foi salvo na pasta '${pastaDestino}'.`);
  } catch (erro) {
    console.error('Erro ao baixar o vídeo:', erro.message);
    process.exit(1);
  }
}

// Função principal
async function main() {
  if (process.argv.length < 3) {
    console.log('Uso: bun youtube_downloader.js URL_DO_VIDEO');
    process.exit(1);
  }

  const url = process.argv[2];
  const info = await obterInfoVideo(url);
  
  console.log(`Título do vídeo: ${info.title}`);
  
  const formatosAudio = mostrarFormatosAudio(info.formats);
  const formatosVideo = mostrarFormatosVideo(info.formats);
  
  if (formatosAudio.length === 0) {
    console.log('Nenhuma faixa de áudio encontrada.');
    process.exit(1);
  }
  
  if (formatosVideo.length === 0) {
    console.log('Nenhum formato de vídeo encontrado.');
    process.exit(1);
  }
  
  // Opção automática ou manual
  const escolha = await perguntar('\nDeseja escolher automaticamente a melhor qualidade? (S/n): ');
  
  let idAudio, idVideo;
  
  if (escolha.trim().toLowerCase() === '' || escolha.trim().toLowerCase() === 's') {
    // Escolha automática
    const idiomaPreferido = await perguntar('Digite o idioma preferido (deixe em branco para português do Brasil): ');
    const idioma = idiomaPreferido.trim() || 'pt-BR';
    
    const resolucaoMaximaInput = await perguntar('Digite a resolução máxima desejada (deixe em branco para 1080p): ');
    let resolucaoMaxima = 1080;
    
    if (resolucaoMaximaInput.trim()) {
      const resolucaoInt = parseInt(resolucaoMaximaInput);
      if (!isNaN(resolucaoInt)) {
        resolucaoMaxima = resolucaoInt;
      } else {
        console.log('Resolução inválida, usando 1080p como padrão.');
      }
    }
    
    idAudio = encontrarMelhorAudio(formatosAudio, idioma);
    idVideo = encontrarMelhorVideo(formatosVideo, resolucaoMaxima);
    
    if (!idAudio) {
      console.log('Não foi possível encontrar uma faixa de áudio adequada.');
      process.exit(1);
    }
    
    if (!idVideo) {
      console.log('Não foi possível encontrar um formato de vídeo adequado.');
      process.exit(1);
    }
    
    console.log('\nSelecionado automaticamente:');
    console.log(`- Áudio: ${idAudio}`);
    console.log(`- Vídeo: ${idVideo}`);
  } else {
    // Escolha manual
    idAudio = await perguntar('\nDigite o ID da faixa de áudio desejada: ');
    idVideo = await perguntar('Digite o ID do formato de vídeo desejado: ');
    
    // Verificar se os IDs existem
    const audioValido = formatosAudio.some(f => f.format_id === idAudio);
    const videoValido = formatosVideo.some(f => f.format_id === idVideo);
    
    if (!audioValido) {
      console.log(`ID de áudio '${idAudio}' não encontrado.`);
      process.exit(1);
    }
    
    if (!videoValido) {
      console.log(`ID de vídeo '${idVideo}' não encontrado.`);
      process.exit(1);
    }
  }
  
  // Criar pasta de destino se não existir
  const pastaDestino = 'downloads';
  if (!existsSync(pastaDestino)) {
    await mkdir(pastaDestino);
  }
  
  // Baixar o vídeo
  await baixarVideo(url, idVideo, idAudio, pastaDestino);
  
  rl.close();
}

main().catch(erro => {
  console.error('Erro:', erro);
  process.exit(1);
}); 