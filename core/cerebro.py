"""
Cérebro do JARVIS v3 — tom de amigo + modo contínuo.

- Respostas variadas e casuais como um amigo que ajuda.
- Normalização de texto (sem acentos) para tolerar variações.
- Filtro de ruído antes de processar (evita reagir a som ambiente curto).
"""

import random
import unicodedata
from core import acoes


# ---------------------------------------------------------------------------
# Normalização
# ---------------------------------------------------------------------------

def _normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().strip()


# ---------------------------------------------------------------------------
# Palavras-chave (já normalizadas, sem acento)
# ---------------------------------------------------------------------------

PALAVRAS_PAUSAR   = ["pausar", "pare de ouvir", "descansar", "fique quieto",
                     "para de ouvir", "silencio", "chega"]
PALAVRAS_SAIR     = ["encerrar jarvis", "desligar jarvis", "fechar jarvis",
                     "sair jarvis", "tchau jarvis", "ate logo jarvis"]
PALAVRAS_ABRIR    = ["abrir", "abra", "abre", "iniciar", "inicia",
                     "lancar", "lanca", "abrir aba", "abre aba"]
PALAVRAS_PESQUISA = ["pesquisar", "pesquise", "buscar", "busque",
                     "procurar", "procure", "googlar", "googla"]
PALAVRAS_HORAS    = ["que horas sao", "que horas", "horas sao",
                     "me diz a hora", "hora atual", "horas"]
PALAVRAS_DATA     = ["que dia", "data de hoje", "qual e a data",
                     "dia de hoje", "que data e hoje"]
PALAVRAS_NOTICIAS = ["noticias", "novidades", "ultimas noticias", "noticia"]
PALAVRAS_CLIMA    = ["clima", "tempo", "previsao do tempo",
                     "vai chover", "temperatura", "como ta o tempo"]
PALAVRAS_PIADA    = ["conta uma piada", "me conta uma piada", "piada",
                     "me faz rir", "fala algo engraçado"]

# Saudações que o JARVIS pode receber (responde de forma amigável)
PALAVRAS_SAUDACAO = ["ola", "oi", "e ai", "salve", "fala", "bom dia",
                     "boa tarde", "boa noite", "tudo bem", "tudo bom",
                     "como voce esta", "como vai"]

# Comprimentos mínimos para não reagir a ruídos curtos (ex: "ah", "oi")
MIN_PALAVRAS = 1   # aceita até 1 palavra (ex: "horas")


# ---------------------------------------------------------------------------
# Respostas variadas — tom de amigo
# ---------------------------------------------------------------------------

FALLBACK = [
    "Hmm, não entendi muito bem. Pode falar de outro jeito?",
    "Eita, essa eu não peguei. Repete aí?",
    "Opa, pode repetir? Acho que não ouvi direito.",
    "Não tô entendendo não, mano. Fala de novo?",
    "Que foi? Não captei. Tenta de outra forma!",
]

SAUDACOES_RESPOSTA = [
    "Oi! Tô aqui, pode falar!",
    "E aí! Que foi? Manda ver.",
    "Salve! Precisando de algo?",
    "Opa! Que posso fazer por você?",
    "Ei! Tô aqui do seu lado. O que precisa?",
    "Oi oi! Pode falar, tô todo ouvidos.",
]

PIADAS = [
    "Por que o computador foi ao médico? Porque estava com vírus! Hahaha!",
    "O que o zero disse pro oito? Boa cinto! Péssima, eu sei, mas me dei bem por isso.",
    "Por que o programador usa óculos? Porque não consegue C# sem eles! Hehe.",
    "Qual é o animal mais antigo? A zebra, porque ainda está em preto e branco!",
    "O que o pato disse pra patinha? Vem morar comigo, é de gratis!",
]


def _contem(norm: str, lista: list) -> bool:
    return any(p in norm for p in lista)


def _comeca_com(norm: str, lista: list) -> bool:
    return any(norm.startswith(p) or norm == p for p in lista)


# ---------------------------------------------------------------------------
# Processador principal
# ---------------------------------------------------------------------------

def processar_comando(texto: str, config: dict) -> str:
    if not texto:
        return random.choice(FALLBACK)

    norm = _normalizar(texto)

    # Ignora fragmentos muito curtos que provavelmente são ruído
    palavras = [p for p in norm.split() if len(p) > 1]
    if len(palavras) < MIN_PALAVRAS:
        return ""   # string vazia = silêncio, main.py não fala nada

    # ── Saudações ────────────────────────────────────────────────────────
    # Verifica se o texto É basicamente uma saudação (poucos tokens)
    if len(palavras) <= 4 and _contem(norm, PALAVRAS_SAUDACAO):
        return random.choice(SAUDACOES_RESPOSTA)

    # ── YouTube (regra prioritária — evita cair no "abrir" depois) ────────
    if "youtube" in norm:
        return acoes.abrir_youtube(texto)

    # ── Sair ──────────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_SAIR):
        return "__SAIR__"

    # ── Pausar ────────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_PAUSAR):
        return "__PAUSAR__"

    # ── Piada ─────────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_PIADA):
        return random.choice(PIADAS)

    # ── Horas ─────────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_HORAS):
        return acoes.dizer_horas()

    # ── Data ──────────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_DATA):
        return acoes.dizer_data()

    # ── Notícias ──────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_NOTICIAS):
        return acoes.abrir_noticias()

    # ── Clima ─────────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_CLIMA):
        return acoes.abrir_clima()

    # ── Pesquisa no Google ────────────────────────────────────────────────
    if _comeca_com(norm, PALAVRAS_PESQUISA) or "no google" in norm or "no bing" in norm:
        termo = norm
        for p in sorted(PALAVRAS_PESQUISA, key=len, reverse=True):
            if termo.startswith(p):
                termo = termo[len(p):].strip()
                break
        termo = (
            termo.replace("no google", "")
                 .replace("no bing", "")
                 .replace("google", "")
                 .strip()
        )
        return acoes.pesquisar_google(termo)

    # ── Abrir aplicativo ──────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_ABRIR):
        apps = config.get("apps", {})
        nome_app = acoes.extrair_nome_app(norm, apps)
        if not nome_app:
            nome_app = acoes.extrair_nome_app(texto.lower(), apps)
        if nome_app:
            return acoes.abrir_app(nome_app, apps)
        return "Cara, não achei esse app na minha lista. Dá pra adicionar no config.json!"

    # ── Fallback ──────────────────────────────────────────────────────────
    return random.choice(FALLBACK)
