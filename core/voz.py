"""
Módulo de voz do JARVIS.

Usa o Edge TTS (vozes neurais gratuitas da Microsoft) como voz principal —
timbre grave e formal, a alternativa mais próxima que existe, sem custo,
de uma voz "estilo assistente de filme". Se não houver internet, cai
automaticamente para a voz offline do Windows (pyttsx3/SAPI5).

IMPORTANTE: não é e não tenta ser uma cópia da voz do ator do filme.
"""

import asyncio
import os
import tempfile
import threading
from typing import Optional

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    from playsound import playsound
    HAS_PLAYSOUND = True
except Exception:
    HAS_PLAYSOUND = False

try:
    import pyttsx3
    _engine_offline = pyttsx3.init()
    HAS_PYTTSX3 = True
except Exception:
    HAS_PYTTSX3 = False

_lock = threading.Lock()


async def _sintetizar_edge(texto: str, voz: str, velocidade: str, tom: str, caminho_saida: str):
    comunicador = edge_tts.Communicate(texto, voz, rate=velocidade, pitch=tom)
    await comunicador.save(caminho_saida)


def _falar_com_edge_tts(texto: str, config_voz: dict) -> bool:
    if not (HAS_EDGE_TTS and HAS_PLAYSOUND):
        return False
    try:
        voz = config_voz.get("voz_edge_tts", "pt-BR-AntonioNeural")
        velocidade = config_voz.get("velocidade", "+0%")
        tom = config_voz.get("tom", "-5Hz")

        # nome único por chamada, para não tentar sobrescrever um arquivo
        # que o player ainda possa estar segurando no Windows
        caminho_tmp = os.path.join(
            tempfile.gettempdir(), f"jarvis_fala_{threading.get_ident()}_{id(texto)}.mp3"
        )
        asyncio.run(_sintetizar_edge(texto, voz, velocidade, tom, caminho_tmp))

        playsound(caminho_tmp, block=True)

        try:
            os.remove(caminho_tmp)
        except OSError:
            pass

        return True
    except Exception as e:
        print(f"[voz] Edge TTS falhou ({e}), usando voz offline de reserva.")
        return False


def _falar_offline(texto: str):
    if not HAS_PYTTSX3:
        print(f"[JARVIS diria]: {texto}")
        return
    _engine_offline.say(texto)
    _engine_offline.runAndWait()


def falar(texto: str, config_voz: Optional[dict] = None, callback_texto=None):
    """
    Fala o texto em voz alta. Sempre imprime também no console/log da GUI
    (via callback_texto, se fornecido) para você acompanhar por escrito.
    """
    config_voz = config_voz or {}
    print(f"[JARVIS] {texto}")
    if callback_texto:
        callback_texto(texto)

    with _lock:
        usar_edge = config_voz.get("usar_edge_tts", True)
        sucesso = False
        if usar_edge:
            sucesso = _falar_com_edge_tts(texto, config_voz)
        if not sucesso:
            _falar_offline(texto)
