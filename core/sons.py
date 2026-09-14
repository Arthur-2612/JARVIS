"""
Módulo de Efeitos Sonoros Sci-Fi (HUD Audio FX) para o JARVIS.

Gera e reproduz efeitos sonoros futuristas locais para feedback auditivo
ao ativar, processar, concluir ou falhar comandos.
"""

import os
import wave
import math
import struct
import threading

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Pasta de armazenamento dos sons sci-fi
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")


def _garantir_diretorio():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR, exist_ok=True)


def _gerar_wav_senoidal(filepath: str, frequencias: list, duracoes_ms: list, volume: float = 0.3, sample_rate: int = 44100):
    """
    Gera um arquivo WAV de síntese sonora futurista combinando frequências e envelopes de áudio.
    """
    if os.path.exists(filepath):
        return

    _garantir_diretorio()

    frames = []
    for freq, dur in zip(frequencias, duracoes_ms):
        num_samples = int(sample_rate * (dur / 1000.0))
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Envelope de ataque e decaimento rápido (fade-in / fade-out)
            envelope = 1.0
            attack_samples = int(num_samples * 0.1)
            decay_samples = int(num_samples * 0.3)
            if i < attack_samples:
                envelope = i / float(attack_samples)
            elif i > (num_samples - decay_samples):
                envelope = (num_samples - i) / float(decay_samples)

            vibrato = math.sin(2 * math.pi * 8 * t) * 5.0 if freq > 500 else 0.0
            val = math.sin(2 * math.pi * (freq + vibrato) * t) * volume * envelope
            # Modulação harmônica leve estilo sci-fi
            val += math.sin(2 * math.pi * (freq * 2.0) * t) * (volume * 0.25) * envelope

            sample_int = int(max(-32768, min(32767, val * 32767)))
            frames.append(struct.pack('<h', sample_int))

    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))


def inicializar_sons():
    """Gera os arquivos WAV dos efeitos sonoros se ainda não existirem."""
    _garantir_diretorio()
    
    # 1. Beep de Ativação ("TRABALHAR" / "JARVIS") -> Tom triplo ascendente cristalino
    p_ativacao = os.path.join(AUDIO_DIR, "ativacao.wav")
    _gerar_wav_senoidal(p_ativacao, [880, 1320, 1760], [40, 40, 70], volume=0.35)

    # 2. Beep de Processando -> Pulso de dados futurista
    p_proc = os.path.join(AUDIO_DIR, "processando.wav")
    _gerar_wav_senoidal(p_proc, [1200, 1600], [30, 40], volume=0.25)

    # 3. Beep de Sucesso -> Acorde harmônico futurista
    p_sucesso = os.path.join(AUDIO_DIR, "sucesso.wav")
    _gerar_wav_senoidal(p_sucesso, [523, 659, 784, 1046], [40, 40, 50, 90], volume=0.35)

    # 4. Beep de Erro / Aviso -> Tom grave e curto
    p_erro = os.path.join(AUDIO_DIR, "erro.wav")
    _gerar_wav_senoidal(p_erro, [350, 220], [60, 90], volume=0.30)


def reproduzir_som(nome: str):
    """
    Reproduz o efeito sonoro de forma assíncrona (não bloqueante).
    Nomes suportados: 'ativacao', 'processando', 'sucesso', 'erro'
    """
    def _play():
        try:
            filepath = os.path.join(AUDIO_DIR, f"{nome}.wav")
            if not os.path.exists(filepath):
                inicializar_sons()

            if HAS_WINSOUND and os.path.exists(filepath):
                winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"[sons] Erro ao reproduzir som {nome}: {e}")

    threading.Thread(target=_play, daemon=True).start()


# Inicializa os arquivos sonoros automaticamente ao importar o módulo
try:
    inicializar_sons()
except Exception as e:
    print(f"[sons] Aviso ao inicializar banco de sons: {e}")
