"""
Módulo de voz do JARVIS v3.

Correção principal: expõe um Event global `falando` que o loop de escuta
em main.py verifica antes de processar áudio. Enquanto o JARVIS está
falando, o microfone fica bloqueado — o JARVIS não ouve a própria voz.

Também adicionamos uma pausa extra de 0.5 s após falar para garantir
que o eco da caixa de som não seja capturado.
"""

import asyncio
import os
import tempfile
import threading
import time
from typing import Optional

# ── Event global: True enquanto JARVIS está falando ─────────────────────────
# O loop de voz em main.py verifica `falando.is_set()` antes de ouvir.
falando = threading.Event()

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


async def _sintetizar_edge(texto: str, voz_nome: str, velocidade: str, tom: str, caminho: str):
    comunicador = edge_tts.Communicate(texto, voz_nome, rate=velocidade, pitch=tom)
    await comunicador.save(caminho)


def _falar_com_edge_tts(texto: str, config_voz: dict) -> bool:
    if not (HAS_EDGE_TTS and HAS_PLAYSOUND):
        return False
    try:
        voz_nome  = config_voz.get("voz_edge_tts", "pt-BR-AntonioNeural")
        velocidade = config_voz.get("velocidade", "+0%")
        tom        = config_voz.get("tom", "-5Hz")

        caminho_tmp = os.path.join(
            tempfile.gettempdir(),
            f"jarvis_fala_{threading.get_ident()}_{id(texto)}.mp3"
        )
        asyncio.run(_sintetizar_edge(texto, voz_nome, velocidade, tom, caminho_tmp))
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
    Fala o texto em voz alta.

    Sinaliza `falando` antes de começar e limpa após terminar + 0.5 s de
    silêncio para o eco da caixa de som não ser capturado pelo microfone.
    """
    config_voz = config_voz or {}
    print(f"[JARVIS] {texto}")
    if callback_texto:
        callback_texto(texto)

    # ── Bloqueia o microfone ────────────────────────────────────────────
    falando.set()
    try:
        with _lock:
            usar_edge = config_voz.get("usar_edge_tts", True)
            sucesso = False
            if usar_edge:
                sucesso = _falar_com_edge_tts(texto, config_voz)
            if not sucesso:
                _falar_offline(texto)
    finally:
        # Pausa extra: deixa o eco dissipar antes de liberar o microfone
        time.sleep(0.6)
        falando.clear()
        # ── Microfone liberado ──────────────────────────────────────────
