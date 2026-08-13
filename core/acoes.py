"""
Ações que o JARVIS pode executar no computador.

Correções v3:
- abrir_youtube: filtra palavras de comando (jarvis, abrir, abra, etc.)
  para não virar termo de busca acidental. Se o restante for vazio,
  apenas abre o YouTube sem buscar — sem duplicar a ação.
- Tom amigável em todas as respostas.
"""

import datetime
import subprocess
import unicodedata
import urllib.parse
import webbrowser

# Palavras que NUNCA devem virar parte de um termo de busca
PALAVRAS_RUIDO = {
    # ativação
    "jarvis", "oi", "ola", "ok", "hey",
    # ação
    "abrir", "abra", "abre", "abrir aba", "abre aba", "iniciar", "inicia",
    "tocar", "toca", "ligar", "liga", "mostrar", "mostra", "colocar", "coloca",
    # ligação
    "pesquisar", "buscar", "procurar", "por", "de", "o", "a", "no", "na",
    "um", "uma", "os", "as", "me", "mim", "para", "pra", "e", "em",
}


# ---------------------------------------------------------------------------
# Normalização
# ---------------------------------------------------------------------------

def _normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().strip()


# ---------------------------------------------------------------------------
# Abrir itens genéricos
# ---------------------------------------------------------------------------

def abrir_item(item: dict) -> bool:
    tipo  = item.get("type")
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
        return f"Cara, não achei '{nome}' na minha lista. Dá pra adicionar no config.json se quiser."
    ok = abrir_item(item)
    if ok:
        return f"Abrindo {nome} pra você!"
    return f"Eita, não consegui abrir o {nome}. Verifica o caminho no config.json."


def extrair_nome_app(texto: str, apps_config: dict):
    """Encontra qual app foi mencionado, tolerando acentos."""
    texto_norm = _normalizar(texto)
    for nome_app in sorted(apps_config.keys(), key=len, reverse=True):
        if nome_app in texto or _normalizar(nome_app) in texto_norm:
            return nome_app
    return None


# ---------------------------------------------------------------------------
# YouTube  ← correção principal da aba dupla
# ---------------------------------------------------------------------------

def abrir_youtube(texto: str) -> str:
    """
    Abre o YouTube. Se houver um termo de busca real (depois de filtrar
    palavras de ruído/comando), abre com a busca. Caso contrário, apenas
    abre a página inicial — uma única ação, sem duplicar.
    """
    norm = _normalizar(texto)

    # Remove a palavra "youtube" e tudo que é ruído/comando
    palavras = [
        p for p in norm.split()
        if p not in PALAVRAS_RUIDO and p != "youtube"
    ]
    termo = " ".join(palavras).strip()

    if termo:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(termo)
        webbrowser.open(url)
        return f"Abrindo o YouTube e já buscando por '{termo}' pra você!"

    webbrowser.open("https://www.youtube.com")
    return "Abrindo o YouTube!"


# ---------------------------------------------------------------------------
# Google
# ---------------------------------------------------------------------------

def pesquisar_google(termo: str) -> str:
    if not termo:
        return "Boa, mas o que você quer que eu pesquise?"
    url = "https://www.google.com/search?q=" + urllib.parse.quote(termo)
    webbrowser.open(url)
    return f"Pesquisando '{termo}' no Google agora!"


# ---------------------------------------------------------------------------
# Informações rápidas — tom amigável
# ---------------------------------------------------------------------------

def dizer_horas() -> str:
    agora = datetime.datetime.now().strftime("%H:%M")
    return f"São {agora}! Perdendo a hora de novo? Brincadeira haha."


def dizer_data() -> str:
    hoje = datetime.datetime.now()
    dias  = ["segunda-feira", "terça-feira", "quarta-feira",
             "quinta-feira", "sexta-feira", "sábado", "domingo"]
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    dia_semana = dias[hoje.weekday()]
    return f"Hoje é {dia_semana}, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}!"


def abrir_noticias() -> str:
    webbrowser.open("https://news.google.com/home?hl=pt-BR&gl=BR&ceid=BR:pt-419")
    return "Aqui estão as últimas notícias pra você ficar por dentro!"


def abrir_clima() -> str:
    webbrowser.open("https://weather.com/pt-BR/tempo/hoje")
    return "Bora ver como tá o tempo lá fora!"
