"""
Módulo de ouvido do JARVIS: escuta o microfone e transforma fala em texto.

Usa o reconhecimento de fala do Google (gratuito, requer internet) via
SpeechRecognition. Retorna None quando não entende ou quando dá timeout,
sem lançar exceção — quem chama só precisa checar "if texto:".
"""

import speech_recognition as sr

_reconhecedor = sr.Recognizer()
_reconhecedor.pause_threshold = 0.8
_reconhecedor.dynamic_energy_threshold = True


def ouvir_comando(
    idioma: str = "pt-BR", timeout: float = 6, phrase_time_limit: float = 7
) -> str | None:
    """
    Escuta o microfone por um comando e retorna o texto reconhecido
    (em minúsculas) ou None se não ouviu/entendeu nada.
    """
    try:
        with sr.Microphone() as fonte:
            _reconhecedor.adjust_for_ambient_noise(fonte, duration=0.4)
            try:
                audio = _reconhecedor.listen(
                    fonte, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            except sr.WaitTimeoutError:
                return None
    except OSError as e:
        print(f"[ouvido] Nenhum microfone encontrado ou erro de áudio: {e}")
        return None

    try:
        texto = _reconhecedor.recognize_google(audio, language=idioma)
        return texto.lower().strip()
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[ouvido] Erro ao contatar o serviço de reconhecimento (precisa de internet): {e}")
        return None
