"""
Cérebro do JARVIS — Assistente virtual elegante e inteligente.

Recursos:
- Persona autêntica inspirada no filme ("Senhor Faria", tom cortês e refinado).
- Controle de tela e automação do Windows (fechar janela/aba, minimizar, maximizar, escrever, copiar/colar, tirar print).
- Efeitos sonoros sci-fi integrados para feedback do HUD.
- Suporte a todos os aplicativos, pesquisas e automações de mídia/hardware.
"""

import random
import re
import unicodedata
from core import acoes, conhecimento, automacao_tela, sons


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
    "desligar", "desliga", "desligue", "encerrar", "encerra", "fechar jarvis",
    "sair", "tchau", "ate logo", "desligar jarvis", "encerrar jarvis",
    "pode desligar", "desligar tudo", "apagar", "desativa", "desativar",
    "parar jarvis", "desligar o jarvis", "fechar o jarvis", "desliga o jarvis",
    "fim", "desligando"
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

PALAVRAS_TELA_CONFIG = [
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
                     "lancar", "lanca", "entrar", "entra",
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
                     "me faz rir", "fala algo engracado"]

PALAVRAS_SAUDACAO = ["ola", "oi", "e ai", "salve", "fala", "bom dia",
                     "boa tarde", "boa noite", "tudo bem", "tudo bom",
                     "como voce esta", "como vai", "trabalhar"]

MIN_PALAVRAS = 1

SAUDACOES_RESPOSTA = [
    "Pois não, Senhor Faria. Em que posso ajudá-lo?",
    "Às suas ordens, Senhor Faria. Como posso ser útil?",
    "Sistemas operacionais e prontos, Senhor Faria. Do que precisa?",
    "Sim, Senhor Faria? Estou à sua inteira disposição.",
    "Olá, Senhor Faria. O que deseja executar agora?"
]

PIADAS = [
    "Por que o computador foi ao médico? Porque estava com vírus! Uma piada simples de meus registros, Senhor Faria.",
    "O que o zero disse para o oito? Belo cinto! Perdoe-me o humor duvidoso, Senhor.",
    "Por que o programador prefere a noite? Porque é no escuro que os bugs se revelam, Senhor Faria."
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

    # Toca som de processamento leve
    sons.reproduzir_som("processando")

    # ── 1. Desligamento prioritário ('desligar', 'encerrar', 'tchau', etc.) ──
    for termo_sair in PALAVRAS_SAIR:
        if norm == termo_sair or f" {termo_sair} " in f" {norm} " or norm.startswith(termo_sair):
            return "__SAIR__"

    # ── 2. Pausar escuta ──────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_PAUSAR):
        return "__PAUSAR__"

    # ── 3. Comandos de Automação e Visão de Tela (Novos) ───────────────────
    if any(p in norm for p in ["tirar print", "capturar tela", "print da tela", "tirar foto da tela"]):
        res = automacao_tela.capturar_tela()
        sons.reproduzir_som("sucesso")
        return res

    if any(p in norm for p in ["visao de tela", "o que tem na tela", "analisar tela", "analisar minha tela"]):
        res = automacao_tela.analisar_visao_tela()
        sons.reproduzir_som("sucesso")
        return res

    if any(p in norm for p in ["fechar janela", "fechar a janela", "fechar programa", "fechar aplicativo"]):
        res = automacao_tela.fechar_janela()
        sons.reproduzir_som("sucesso")
        return res

    if any(p in norm for p in ["fechar aba", "fechar a aba"]):
        res = automacao_tela.fechar_aba()
        sons.reproduzir_som("sucesso")
        return res

    if any(p in norm for p in ["minimizar janela", "minimizar a janela", "minimizar tela"]):
        res = automacao_tela.minimizar_janela()
        sons.reproduzir_som("sucesso")
        return res

    if any(p in norm for p in ["minimizar tudo", "minimizar todas as janelas", "mostrar area de trabalho"]):
        res = automacao_tela.minimizar_tudo()
        sons.reproduzir_som("sucesso")
        return res

    if any(p in norm for p in ["maximizar janela", "maximizar a janela", "maximizar tela"]):
        res = automacao_tela.maximizar_janela()
        sons.reproduzir_som("sucesso")
        return res

    if any(p in norm for p in ["alternar janela", "trocar de janela", "mudar de janela"]):
        res = automacao_tela.alternar_janela()
        sons.reproduzir_som("sucesso")
        return res

    if _comeca_com(norm, ["escrever ", "digitar ", "escreva ", "digite "]):
        # Extrai o texto a ser digitado mantendo acentuação original
        prefixo_match = re.match(r'^(escrever|digitar|escreva|digite)\s+', texto, re.IGNORECASE)
        texto_digitar = texto[prefixo_match.end():].strip() if prefixo_match else texto
        res = automacao_tela.escrever_texto(texto_digitar)
        sons.reproduzir_som("sucesso")
        return res

    if norm in ["copiar", "copia isso", "copiar conteudo"]:
        res = automacao_tela.copiar()
        sons.reproduzir_som("sucesso")
        return res

    if norm in ["colar", "cola isso", "colar conteudo"]:
        res = automacao_tela.colar()
        sons.reproduzir_som("sucesso")
        return res

    if norm in ["selecionar tudo", "seleciona tudo"]:
        res = automacao_tela.selecionar_tudo()
        sons.reproduzir_som("sucesso")
        return res

    if "rolar para baixo" in norm or "scroll para baixo" in norm:
        res = automacao_tela.rolar_tela("baixo")
        sons.reproduzir_som("sucesso")
        return res

    if "rolar para cima" in norm or "scroll para cima" in norm:
        res = automacao_tela.rolar_tela("cima")
        sons.reproduzir_som("sucesso")
        return res

    # ── 4. Análise do Computador / Diagnóstico ────────────────────────────
    if _contem(norm, PALAVRAS_ANALISE) or ("analis" in norm and any(k in norm for k in ["computador", "pc", "funcionalidade", "sistema"])):
        sons.reproduzir_som("sucesso")
        return acoes.analisar_sistema()

    # ── 5. Controle de Mídia (Pausar / Despausar Vídeo) ────────────────────
    if _contem(norm, PALAVRAS_MIDIA) or ("video" in norm and any(k in norm for k in ["pausar", "despausar", "tocar", "play", "pausa"])):
        sons.reproduzir_som("sucesso")
        return acoes.alternar_midia()

    # ── 6. Controle de Volume Master ──────────────────────────────────────
    if _contem(norm, PALAVRAS_VOLUME) or "abaixar volume" in norm or "aumentar volume" in norm:
        numeros = re.findall(r'\d+', texto)
        sons.reproduzir_som("sucesso")
        if numeros:
            val = int(numeros[0])
            return acoes.definir_volume(val)
        if any(k in norm for k in ["aumentar", "subir", "mais"]):
            return acoes.alterar_volume_relativo(15)
        if any(k in norm for k in ["abaixar", "diminuir", "menos"]):
            return acoes.alterar_volume_relativo(-15)
        if any(k in norm for k in ["mudo", "mutar", "silenciar"]):
            return acoes.definir_volume(0)

    # ── 7. Controle de Brilho da Tela ─────────────────────────────────────
    if _contem(norm, PALAVRAS_BRILHO):
        numeros = re.findall(r'\d+', texto)
        sons.reproduzir_som("sucesso")
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

    # ── 8. Configurações de Exibição ──────────────────────────────────────
    if _contem(norm, PALAVRAS_TELA_CONFIG):
        sons.reproduzir_som("sucesso")
        return acoes.abrir_configuracoes_tela()

    # ── 9. Curiosidades ───────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_CURIOSIDADE):
        sons.reproduzir_som("sucesso")
        return conhecimento.obter_curiosidade()

    # ── 10. Piadas ────────────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_PIADA):
        sons.reproduzir_som("sucesso")
        return random.choice(PIADAS)

    # ── 11. Horas e Data ──────────────────────────────────────────────────
    if _contem(norm, PALAVRAS_HORAS):
        sons.reproduzir_som("sucesso")
        return acoes.dizer_horas()

    if _contem(norm, PALAVRAS_DATA):
        sons.reproduzir_som("sucesso")
        return acoes.dizer_data()

    # ── 12. Notícias e Clima ──────────────────────────────────────────────
    if _contem(norm, PALAVRAS_NOTICIAS):
        sons.reproduzir_som("sucesso")
        return acoes.abrir_noticias()

    if _contem(norm, PALAVRAS_CLIMA):
        sons.reproduzir_som("sucesso")
        return acoes.abrir_clima()

    # ── 13. Saudações ─────────────────────────────────────────────────────
    if len(palavras) <= 3 and _contem(norm, PALAVRAS_SAUDACAO):
        sons.reproduzir_som("sucesso")
        return random.choice(SAUDACOES_RESPOSTA)

    # ── 14. YouTube ───────────────────────────────────────────────────────
    if "youtube" in norm:
        sons.reproduzir_som("sucesso")
        return acoes.abrir_youtube(texto)

    # ── 15. Pesquisa explícita ────────────────────────────────────────────
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
            sons.reproduzir_som("sucesso")
            return acoes.pesquisar_google(termo)

    # ── 16. Aplicativos e sites ───────────────────────────────────────────
    apps = config.get("apps", {})
    nome_app = acoes.extrair_nome_app(norm, apps)
    if not nome_app:
        nome_app = acoes.extrair_nome_app(texto.lower(), apps)

    if nome_app:
        sons.reproduzir_som("sucesso")
        return acoes.abrir_app(nome_app, apps)

    if _contem(norm, PALAVRAS_ABRIR):
        # Resposta refinada e elegante (NUNCA menciona config.json)
        sons.reproduzir_som("erro")
        return "Lamento, Senhor Faria, mas não encontrei este aplicativo registrado em meus arquivos. Deseja que eu tente pesquisá-lo ou localizá-lo no sistema?"

    # ── 17. Perguntas gerais e conhecimentos (Wikipédia / Inteligência) ───
    resposta_conhecimento = conhecimento.responder_pergunta(texto)
    if resposta_conhecimento:
        sons.reproduzir_som("sucesso")
        return resposta_conhecimento

    # Se parecer uma pergunta geral ("o que", "quem", "como", "onde", "por que"), pesquisa
    if any(q in norm for q in ["o que", "quem", "como", "onde", "por que", "qual", "quanto"]):
        sons.reproduzir_som("sucesso")
        return acoes.pesquisar_google(texto)

    # ── Fallback amigável com a persona ───────────────────────────────────
    sons.reproduzir_som("sucesso")
    return "Estou à sua disposição, Senhor Faria. Pode me solicitar buscas, automações de tela ou comandos do sistema."
