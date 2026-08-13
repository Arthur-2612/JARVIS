"""
Ações que o JARVIS pode executar no computador: abrir programas,
abrir o YouTube, pesquisar no Google, dizer as horas, etc.
"""

import datetime
import subprocess
import urllib.parse
import webbrowser


def abrir_item(item: dict) -> bool:
    tipo = item.get("type")
    valor = item.get("value")
    try:
        if tipo == "path":
            subprocess.Popen([valor])
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
    for nome_app in apps_config:
        if nome_app in texto:
            return nome_app
    return None


PALAVRAS_DE_LIGACAO_YOUTUBE = ["tocar", "toca", "pesquisar", "buscar", "procurar", "por", "de", "o", "a"]


def abrir_youtube(texto: str) -> str:
    """
    Regra fixa: qualquer comando que mencione 'youtube' abre o YouTube de
    verdade (youtube.com). Se houver um termo de busca junto ('tocar X no
    youtube', 'youtube pesquisar X'), abre já com a busca feita.
    """
    partes = texto.split("youtube")
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
    if not termo:
        return "O que você quer que eu pesquise, senhor?"
    url = "https://www.google.com/search?q=" + urllib.parse.quote(termo)
    webbrowser.open(url)
    return f"Pesquisando {termo} no Google."


def dizer_horas() -> str:
    agora = datetime.datetime.now().strftime("%H:%M")
    return f"Agora são {agora}, senhor."
