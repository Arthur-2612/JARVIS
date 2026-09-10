"""
Ações que o JARVIS pode executar no computador: abrir programas,
abrir o YouTube, pesquisar no Google, dizer as horas, etc.
"""

import datetime
import re
import shutil
import subprocess
import urllib.parse
import webbrowser


def _normalizar_texto(texto: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", texto.lower()).strip()


def abrir_item(item: dict) -> bool:
    tipo = item.get("type")
    valor = item.get("value")
    try:
        if tipo == "path":
            caminho = shutil.which(valor) or valor
            subprocess.Popen([caminho])
        elif tipo == "command":
            subprocess.Popen(valor, shell=True)
        elif tipo == "url":
            webbrowser.open(valor)
        else:
            return False
        return True
    except Exception as e:
        print(f"[acoes] Erro ao abrir '{valor}': {e}")
        return False


def abrir_app(nome: str, apps_config: dict) -> str:
    item = apps_config.get(nome)
    if not item:
        return f"Não encontrei '{nome}' na minha lista de aplicativos, senhor."
    ok = abrir_item(item)
    if ok:
        return f"Abrindo {nome}."
    return f"Não consegui abrir {nome}. Verifique o caminho no config.json."


def extrair_nome_app(texto: str, apps_config: dict):
    """Encontra qual app configurado foi mencionado no texto reconhecido."""
    texto_normalizado = _normalizar_texto(texto)
    for nome_app in apps_config:
        if _normalizar_texto(nome_app) in texto_normalizado:
            return nome_app
    return None


PALAVRAS_DE_LIGACAO_YOUTUBE = ["tocar", "toca", "pesquisar", "buscar", "procurar", "por", "de", "o", "a", "no", "na", "do", "da", "sobre"]


def abrir_youtube(texto: str) -> str:
    """Abre o YouTube e, quando houver, busca por um termo informado."""
    texto_normalizado = _normalizar_texto(texto)
    partes = texto_normalizado.split("youtube")
    resto = " ".join(partes).strip()

    palavras = [p for p in resto.split() if p not in PALAVRAS_DE_LIGACAO_YOUTUBE]
    termo = " ".join(palavras).strip()

    if termo:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(termo)
        webbrowser.open(url)
        return f"Abrindo o YouTube e buscando por {termo}."

    webbrowser.open("https://www.youtube.com")
    return "Abrindo o YouTube."


def pesquisar_google(termo: str) -> str:
    termo = (termo or "").strip()
    if not termo:
        return "O que você quer que eu pesquise, senhor?"
    url = "https://www.google.com/search?q=" + urllib.parse.quote(termo)
    webbrowser.open(url)
    return f"Pesquisando {termo} no Google."


def dizer_horas() -> str:
    agora = datetime.datetime.now().strftime("%H:%M")
    return f"Agora são {agora}, senhor."


dizer_horas = dizer_horas
