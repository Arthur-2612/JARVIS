"""
Cérebro do JARVIS: pega o texto reconhecido pelo ouvido e decide o que fazer.

Retorna sempre uma string (resposta falada) — exceto para os sinais
especiais "__PAUSAR__" e "__SAIR__", que o main.py trata separadamente.
"""

from core import acoes

PALAVRAS_PAUSAR = ["pausar", "pare de ouvir", "descansar", "fique quieto"]
PALAVRAS_SAIR = ["encerrar jarvis", "desligar jarvis", "fechar jarvis"]
PALAVRAS_ABRIR = ["abrir", "abra", "abre"]
PALAVRAS_PESQUISA = ["pesquisar", "pesquise", "buscar", "busque", "procurar", "procure"]
PALAVRAS_HORAS = ["que horas são", "horas são", "que horas", "me diga a hora"]


def processar_comando(texto: str, config: dict) -> str:
    if not texto:
        return "Não entendi, pode repetir?"

    texto = texto.lower().strip()

    # Regra explícita e prioritária: qualquer menção ao YouTube abre o
    # YouTube de verdade, nunca uma busca genérica no navegador.
    if "youtube" in texto:
        return acoes.abrir_youtube(texto)

    if any(p in texto for p in PALAVRAS_SAIR):
        return "__SAIR__"

    if any(p in texto for p in PALAVRAS_PAUSAR):
        return "__PAUSAR__"

    if any(p in texto for p in PALAVRAS_HORAS):
        return acoes.dizer_horas()

    if any(texto.startswith(p) for p in PALAVRAS_PESQUISA):
        termo = texto
        for p in PALAVRAS_PESQUISA:
            termo = termo.replace(p, "", 1)
        termo = termo.replace(" no google", "").replace("google", "").strip()
        return acoes.pesquisar_google(termo)

    if any(p in texto for p in PALAVRAS_ABRIR):
        apps = config.get("apps", {})
        nome_app = acoes.extrair_nome_app(texto, apps)
        if nome_app:
            return acoes.abrir_app(nome_app, apps)
        return "Não encontrei esse aplicativo na minha lista. Você pode adicioná-lo no config.json."

    return "Não entendi o comando, senhor. Pode repetir de outra forma?"
