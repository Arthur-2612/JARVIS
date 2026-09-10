"""
Cérebro do JARVIS: pega o texto reconhecido pelo ouvido e decide o que fazer.

Retorna sempre uma string (resposta falada) — exceto para os sinais
especiais "__PAUSAR__" e "__SAIR__", que o main.py trata separadamente.
"""

import re

from core import acoes

PALAVRAS_PAUSAR = ["pausar", "pare de ouvir", "descansar", "fique quieto"]
PALAVRAS_SAIR = ["encerrar jarvis", "desligar jarvis", "fechar jarvis", "encerrar", "desligar", "fechar"]
PALAVRAS_ABRIR = ["abrir", "abra", "abre", "abri", "abrir o", "abrir a"]
PALAVRAS_PESQUISA = ["pesquisar", "pesquise", "buscar", "busque", "procurar", "procure", "pesquisa"]
PALAVRAS_HORAS = ["que horas sao", "horas sao", "que horas", "me diga a hora", "me diga as horas"]
PALAVRAS_FILTRO = ["jarvis", "por favor", "porfavor", "me", "meu", "minha", "a", "o", "os", "as", "do", "da", "de", "para", "sobre"]


def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = texto.replace("’", "'")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    for palavra in PALAVRAS_FILTRO:
        texto = re.sub(rf"\b{re.escape(palavra)}\b", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def _tem_palavra(texto: str, palavras: list[str]) -> bool:
    return any(p in texto for p in palavras)


def _extrair_termo_pesquisa(texto: str) -> str:
    texto = normalizar_texto(texto)
    for padrao in PALAVRAS_PESQUISA:
        if padrao in texto:
            resto = texto.split(padrao, 1)[1] if padrao in texto else ""
            resto = resto.replace("no google", "").replace("google", "")
            resto = re.sub(r"\b(?:sobre|a|o|os|as|do|da|de|em|para)\b", " ", resto)
            return re.sub(r"\s+", " ", resto).strip()
    return ""


def processar_comando(texto: str, config: dict) -> str:
    if not texto:
        return "Não entendi, pode repetir?"

    texto = normalizar_texto(texto)
    if not texto:
        return "Não entendi, pode repetir?"

    if "youtube" in texto:
        return acoes.abrir_youtube(texto)

    if _tem_palavra(texto, PALAVRAS_SAIR):
        return "__SAIR__"

    if _tem_palavra(texto, PALAVRAS_PAUSAR):
        return "__PAUSAR__"

    if _tem_palavra(texto, PALAVRAS_HORAS):
        return acoes.dizer_horas()

    if _tem_palavra(texto, PALAVRAS_PESQUISA):
        termo = _extrair_termo_pesquisa(texto)
        return acoes.pesquisar_google(termo)

    if _tem_palavra(texto, PALAVRAS_ABRIR):
        apps = config.get("apps", {})
        nome_app = acoes.extrair_nome_app(texto, apps)
        if nome_app:
            return acoes.abrir_app(nome_app, apps)
        return "Não encontrei esse aplicativo na minha lista. Você pode adicioná-lo no config.json."

    return "Não entendi o comando, senhor. Pode repetir de outra forma?"
