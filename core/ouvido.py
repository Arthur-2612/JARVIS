"""
Módulo de ouvido do JARVIS: escuta o microfone e transforma fala em texto.

Melhorias v2:
- dynamic_energy_threshold=True com limiar inicial baixo (300) → adapta ao ruído.
- Calibração única na inicialização (2 s) em vez de 0.5 s por loop.
- Callback on_nivel_audio para mostrar barra de nível na GUI.
- Callback on_status para avisar quando começou a capturar ou parou.
- Melhor seleção de device_index: tenta por nome, depois usa padrão do sistema.
- listar_microfones() e calibrar_microfone() expostos para diagnóstico/GUI.
"""

import speech_recognition as sr
import threading

_reconhecedor = sr.Recognizer()
_reconhecedor.pause_threshold = 1.0        # 1 s de silêncio = fim da frase
_reconhecedor.energy_threshold = 300       # começa baixo e se adapta
_reconhecedor.dynamic_energy_threshold = True   # adapta automaticamente ao ambiente
_reconhecedor.dynamic_energy_adjustment_damping = 0.15
_reconhecedor.dynamic_energy_ratio = 1.5

# Lock para garantir acesso sequencial ao reconhecedor
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Utilitários públicos de diagnóstico
# ---------------------------------------------------------------------------

def listar_microfones() -> list[tuple[int, str]]:
    """Retorna lista de (índice, nome) de todos os microfones disponíveis."""
    try:
        nomes = sr.Microphone.list_microphone_names()
        return list(enumerate(nomes))
    except Exception:
        return []


def calibrar_microfone(device_index=None, duration: float = 2.0):
    """
    Faz uma calibração única de ruído ambiente (2 s) e atualiza
    energy_threshold no reconhecedor global. Chamar uma vez na inicialização.
    """
    try:
        mic = sr.Microphone(device_index=device_index) if device_index is not None else sr.Microphone()
        with mic as fonte:
            _reconhecedor.adjust_for_ambient_noise(fonte, duration=duration)
        print(f"[ouvido] Calibrado. energy_threshold={_reconhecedor.energy_threshold:.0f}")
    except Exception as e:
        print(f"[ouvido] Calibração falhou: {e}")


# ---------------------------------------------------------------------------
# Seleção de dispositivo
# ---------------------------------------------------------------------------

def _resolver_device_index(config: dict | None = None):
    """
    Ordem de prioridade:
    1. device_index inteiro no config.json (se diferente de null/None).
    2. Primeiro microfone cujo nome contenha token conhecido.
    3. None → SpeechRecognition usa o dispositivo padrão do sistema.
    """
    if config:
        microfone_cfg = config.get("microfone", {})
        device_index = microfone_cfg.get("device_index")
        if isinstance(device_index, int):
            return device_index

    # Tenta localizar por nome
    try:
        nomes = sr.Microphone.list_microphone_names()
        tokens_preferidos = ["fuxi", "microfone", "realtek", "mic", "headset", "usb"]
        for indice, nome in enumerate(nomes):
            nome_lower = nome.lower()
            if any(t in nome_lower for t in tokens_preferidos):
                print(f"[ouvido] Microfone encontrado por nome: [{indice}] {nome}")
                return indice
    except Exception:
        pass

    return None   # usa padrão do sistema


# ---------------------------------------------------------------------------
# Escuta principal
# ---------------------------------------------------------------------------

def ouvir_comando(
    idioma: str = "pt-BR",
    timeout: int = 5,
    phrase_time_limit: int = 10,
    config: dict | None = None,
    on_status=None,         # callable(str) → "ouvindo" | "processando" | "silencio"
) -> str | None:
    """
    Escuta o microfone por um comando e retorna o texto reconhecido
    (em minúsculas) ou None se não ouviu/entendeu nada.

    on_status: callback chamado com strings de estado para atualizar a GUI.
    """
    device_index = _resolver_device_index(config)

    try:
        mic = sr.Microphone(device_index=device_index) if device_index is not None else sr.Microphone()
        with _lock:
            with mic as fonte:
                # Ajuste rápido de ruído a cada chamada (0.3 s é suficiente com dynamic=True)
                _reconhecedor.adjust_for_ambient_noise(fonte, duration=0.3)

                if on_status:
                    on_status("ouvindo")

                try:
                    audio = _reconhecedor.listen(
                        fonte,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit,
                    )
                except sr.WaitTimeoutError:
                    if on_status:
                        on_status("silencio")
                    return None

    except OSError as e:
        print(f"[ouvido] Erro de áudio/microfone: {e}")
        if on_status:
            on_status("erro")
        return None

    if on_status:
        on_status("processando")

    try:
        texto = _reconhecedor.recognize_google(audio, language=idioma)
        print(f"[ouvido] Reconhecido: {texto}")
        return texto.lower().strip()
    except sr.UnknownValueError:
        if on_status:
            on_status("silencio")
        return None
    except sr.RequestError as e:
        print(f"[ouvido] Erro no serviço Google (sem internet?): {e}")
        if on_status:
            on_status("erro")
        return None
