"""
Cérebro do JARVIS v5 — assistente virtual inteligente completo.

- Responde curiosidades gerais e perguntas sobre quase tudo (Wikipédia API + banco de dados).
- Controle avançado de hardware: volume por %, brilho, pausar/despausar mídia, tamanho/resolução de tela.
- Análise e diagnóstico do computador em tempo real.
- Suporte a desligamento instantâneo por qualquer palavra relacionada ('desligar', 'desliga', 'encerrar', 'tchau', 'fechar', etc.).
- Suporte a todos os apps e sites do config.json.
- Fallback inteligente com pesquisa automática quando necessário.
"""

import random
import re
import unicodedata
from core import acoes, conhecimento


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

PALAVRAS_SAIR     = [
    "desligar", "desliga", "desligue", "encerrar", "encerra", "fechar", "fecha",
    "sair", "tchau", "ate logo", "desligar jarvis", "encerrar jarvis",
    "fechar jarvis", "pode desligar", "desligar tudo", "apagar",
    "desativa", "desativar", "parar jarvis", "desligar o jarvis",
    "fechar o jarvis", "desliga o jarvis", "fim", "desligando"
]

PALAVRAS_PAUSAR   = ["pausar jarvis", "pare de ouvir", "descansar", "fique quieto",
                     "para de ouvir", "silencio", "chega", "pausa o jarvis"]

PALAVRAS_MIDIA    = [
    "pausar video", "despausar video", "pausar o video", "despausar o video",
    "pausa o video", "tocar video", "play no video", "da play", "dar play",
    "pausar musica", "despausar musica", "pausar midia", "despausar midia",
    "pausar o filme", "despausar o filme", "pausa o filme", "tocar midia",
    "pausa o som", "despausa o som"
]

PALAVRAS_VOLUME   = ["volume", "som", "audio"]

PALAVRAS_BRILHO   = ["brilho", "luminosidade", "luz da tela"]

PALAVRAS_TELA     = [
    "tamanho da minha tela", "tamanho da tela", "resolucao",
    "resolucao da tela", "configuracoes de tela", "ajustar tela"
]

PALAVRAS_ANALISE  = [
    "analise todas", "analise o computador", "analise meu computador",
    "analisar computador", "analisar o computador", "analise as funcionalidades",
    "diagnostico do sistema", "diagnostico do computador", "status do pc",
    "status do computador", "como esta meu computador", "como ta meu computador",
    "como esta meu pc", "analise o pc", "verificar computador", "analisar sistema"
]

PALAVRAS_ABRIR    = ["abrir", "abra", "abre", "iniciar", "inicia",
                     "lancar", "lanca", "abrir aba", "abre aba", "entrar", "entra",
                     "acessar", "acesse", "vai pro", "vai para"]

PALAVRAS_PESQUISA = ["pesquisar", "pesquise", "buscar", "busque",
                     "procurar", "procure", "googlar", "googla"]

PALAVRAS_CURIOSIDADE = [
    "curiosidade", "curiosidades", "sabia que", "fato curioso",
    "me conta algo", "me ensina algo", "uma curiosidade",
    "conta uma curiosidade", "fala uma curiosidade", "sabe de algo legal"
]

PALAVRAS_HORAS    = ["que horas sao", "que horas", "horas sao",
                     "me diz a hora", "hora atual", "horas"]

PALAVRAS_DATA     = ["que dia", "data de hoje", "qual e a data",
                     "dia de hoje", "que data e hoje"]

PALAVRAS_NOTICIAS = ["noticias", "novidades", "ultimas noticias", "noticia"]

PALAVRAS_CLIMA    = ["clima", "tempo", "previsao do tempo",
                     "vai chover", "temperatura", "como ta o tempo"]

PALAVRAS_PIADA    = ["conta uma piada", "me conta uma piada", "piada",
                     "me faz rir", "fala algo engraçado"]

PALAVRAS_SAUDACAO = ["ola", "oi", "e ai", "salve", "fala", "bom dia",
                     "boa tarde", "boa noite", "tudo bem", "tudo bom",
                     "como voce esta", "como vai"]

MIN_PALAVRAS = 1

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
        return ""

    norm = _normalizar(texto)

    palavras = [p for p in norm.split() if len(p) > 1]
    if len(palavras) < MIN_PALAVRAS:
        return ""

    # ── 1. Desligamento prioritário ('desligar', 'encerrar', 'tchau', etc.) ──
    for termo_sair in PALAVRAS_SAIR:
        if norm == termo_sair or f" {termo_sair} " in f" {norm} " or norm.startswith(termo_sair):
            return "__SAIR__"

    # ── 2. Pausar escuta ──────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_PAUSAR):
        return "__PAUSAR__"

    # ── 3. Análise do Computador / Diagnóstico ────────────────────────────
    if _contem(norm, PALAVRAS_ANALISE) or ("analis" in norm and any(k in norm for k in ["computador", "pc", "funcionalidade", "sistema"])):
        return acoes.analisar_sistema()

    # ── 4. Controle de Mídia (Pausar / Despausar Vídeo) ────────────────────
    if _contem(norm, PALAVRAS_MIDIA) or ("video" in norm and any(k in norm for k in ["pausar", "despausar", "tocar", "play", "pausa"])):
        return acoes.alternar_midia()

    # ── 5. Controle de Volume Master ──────────────────────────────────────
    if _contem(norm, PALAVRAS_VOLUME) or "abaixar volume" in norm or "aumentar volume" in norm:
        numeros = re.findall(r'\d+', texto)
        if numeros:
            val = int(numeros[0])
            return acoes.definir_volume(val)
        if any(k in norm for k in ["aumentar", "subir", "mais"]):
            return acoes.alterar_volume_relativo(15)
        if any(k in norm for k in ["abaixar", "diminuir", "menos"]):
            return acoes.alterar_volume_relativo(-15)
        if any(k in norm for k in ["mudo", "mutar", "silenciar"]):
            return acoes.definir_volume(0)

    # ── 6. Controle de Brilho da Tela ─────────────────────────────────────
    if _contem(norm, PALAVRAS_BRILHO):
        numeros = re.findall(r'\d+', texto)
        if numeros:
            val = int(numeros[0])
            return acoes.ajustar_brilho(val)
        if any(k in norm for k in ["aumentar", "mais"]):
            return acoes.ajustar_brilho(80)
        if any(k in norm for k in ["diminuir", "abaixar", "menos"]):
            return acoes.ajustar_brilho(30)
        if "maximo" in norm:
            return acoes.ajustar_brilho(100)
        return acoes.ajustar_brilho(70)

    # ── 7. Configurações de Exibição / Resolução de Tela ───────────────────
    if _contem(norm, PALAVRAS_TELA):
        return acoes.abrir_configuracoes_tela()

    # ── 8. Curiosidades ───────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_CURIOSIDADE):
        return conhecimento.obter_curiosidade()

    # ── 9. Piadas ─────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_PIADA):
        return random.choice(PIADAS)

    # ── 10. Horas e Data ──────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_HORAS):
        return acoes.dizer_horas()

    if _contem(norm, PALAVRAS_DATA):
        return acoes.dizer_data()

    # ── 11. Notícias e Clima ──────────────────────────────────────────────
    if _contem(norm, PALAVRAS_NOTICIAS):
        return acoes.abrir_noticias()

    if _contem(norm, PALAVRAS_CLIMA):
        return acoes.abrir_clima()

    # ── 12. Saudações ─────────────────────────────────────────────────────
    if len(palavras) <= 3 and _contem(norm, PALAVRAS_SAUDACAO):
        return random.choice(SAUDACOES_RESPOSTA)

    # ── 13. YouTube ───────────────────────────────────────────────────────
    if "youtube" in norm:
        return acoes.abrir_youtube(texto)

    # ── 14. Pesquisa explícita ────────────────────────────────────────────
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
        if termo:
            return acoes.pesquisar_google(termo)

    # ── 15. Aplicativos e sites do config.json ────────────────────────────
    apps = config.get("apps", {})
    nome_app = acoes.extrair_nome_app(norm, apps)
    if not nome_app:
        nome_app = acoes.extrair_nome_app(texto.lower(), apps)

    if nome_app:
        return acoes.abrir_app(nome_app, apps)

    if _contem(norm, PALAVRAS_ABRIR):
        return "Cara, não achei esse app na minha lista. Dá pra adicionar no config.json!"

    # ── 16. Perguntas gerais e conhecimentos (Wikipédia / Inteligência) ───
    resposta_conhecimento = conhecimento.responder_pergunta(texto)
    if resposta_conhecimento:
        return resposta_conhecimento

    # Se a frase parecer uma pergunta ("o que", "quem", "como", "onde", "por que", "?"), pesquisa automaticamente
    if any(q in norm for q in ["o que", "quem", "como", "onde", "por que", "qual", "quanto"]):
        return acoes.pesquisar_google(texto)

    # ── Fallback amigável ─────────────────────────────────────────────────
    return "Eu tô aqui! Pode me perguntar qualquer curiosidade, pedir pra abrir um site ou me mandar pesquisar!"
