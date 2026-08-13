"""
Ações que o JARVIS pode executar no computador.

Melhorias v4:
- Suporte a aliases e sinônimos estendidos (email, chat gpt, zap, insta, etc.).
- Verificação inteligente de executáveis em disco antes de subprocess.
- Respostas amigáveis e descontraídas.
"""

import datetime
import os
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
    "entra", "entrar", "vai", "ir", "acessar", "acesse",
    # ligação
    "pesquisar", "buscar", "procurar", "por", "de", "o", "a", "no", "na",
    "um", "uma", "os", "as", "me", "mim", "para", "pra", "e", "em",
}

# Mapeamento estendido de sinônimos/aliases para chaves padrão
ALIASES_CUSTOM = {
    "email": "email",
    "e-mail": "e-mail",
    "correio": "email",
    "correio eletronico": "email",
    "chat gpt": "chat gpt",
    "chatgpt": "chatgpt",
    "gpt": "gpt",
    "zap": "zap",
    "whats": "whats",
    "whatsapp": "whatsapp",
    "insta": "insta",
    "instagram": "instagram",
    "face": "face",
    "facebook": "facebook",
    "musica": "musica",
    "spotify": "spotify",
    "navegador": "navegador",
    "internet": "internet",
    "bloco de notas": "bloco de notas",
    "bloco de nota": "bloco de nota",
    "notepad": "notepad",
    "calculadora": "calculadora",
    "calc": "calc",
    "explorer": "explorer",
    "meus arquivos": "meus arquivos",
    "pastas": "pastas",
    "pasta": "pasta",
    "configuracao": "configuracao",
    "configuracoes": "configuracoes",
    "prime": "prime",
    "amazon prime": "amazon prime",
    "planilha": "planilha",
    "planilhas": "planilhas",
    "slides": "slides",
    "apresentacao": "apresentacao",
    "docs": "docs",
    "documento": "docs",
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
            if os.path.exists(valor):
                subprocess.Popen([valor])
                return True
            else:
                print(f"[acoes] Executável não encontrado em: {valor}")
                return False
        elif tipo == "command":
            subprocess.Popen(valor, shell=True)
            return True
        elif tipo == "url":
            webbrowser.open(valor)
            return True
        return False
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
    
    # Se falhou um caminho em disco (ex: app não instalado), verifica se há URL fallback
    if item.get("type") == "path":
        nome_url = f"{nome} web"
        if nome_url in apps_config:
            abrir_item(apps_config[nome_url])
            return f"Não achei o aplicativo instalado, então abri a versão web do {nome}!"

    return f"Eita, não consegui abrir o {nome}. Verifica o caminho no config.json."


def extrair_nome_app(texto: str, apps_config: dict) -> str | None:
    """
    Encontra qual app configurado foi mencionado no texto reconhecido.
    Testa tanto chaves diretas quanto aliases e normalização sem acentos.
    """
    texto_norm = _normalizar(texto)

    # 1. Busca por chaves do config.json ordenadas pelo tamanho (maiores primeiro)
    chaves_ordenadas = sorted(apps_config.keys(), key=len, reverse=True)
    for nome_app in chaves_ordenadas:
        nome_norm = _normalizar(nome_app)
        # Verifica se o nome aparece como palavra exata ou subfrase
        if f" {nome_norm} " in f" {texto_norm} " or nome_norm == texto_norm:
            return nome_app

    # 2. Busca permissiva (contém no texto)
    for nome_app in chaves_ordenadas:
        nome_norm = _normalizar(nome_app)
        if len(nome_norm) >= 3 and nome_norm in texto_norm:
            return nome_app

    return None


# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------

def abrir_youtube(texto: str) -> str:
    norm = _normalizar(texto)

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
