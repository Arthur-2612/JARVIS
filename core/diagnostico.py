"""
Módulo de diagnóstico do JARVIS.

Detecta todos os microfones disponíveis no sistema, testa qual responde
e permite salvar o device_index correto no config.json.
"""

import json
from pathlib import Path
import speech_recognition as sr


def listar_microfones() -> list[tuple[int, str]]:
    """Retorna lista de (índice, nome) de todos os microfones disponíveis."""
    try:
        nomes = sr.Microphone.list_microphone_names()
        return [(i, n) for i, n in enumerate(nomes)]
    except Exception as e:
        print(f"[diagnostico] Erro ao listar microfones: {e}")
        return []


def salvar_device_index(config_path: Path, device_index: int | None):
    """Salva o device_index escolhido no config.json."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg.setdefault("microfone", {})["device_index"] = device_index
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print(f"[diagnostico] device_index={device_index} salvo em {config_path}")
    except Exception as e:
        print(f"[diagnostico] Erro ao salvar config: {e}")
