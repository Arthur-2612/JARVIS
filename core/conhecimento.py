"""
Módulo de Conhecimento e Curiosidades do JARVIS.

Recursos:
- Banco de curiosidades impressionantes sobre ciência, espaço, história e natureza.
- Respostas rápidas para perguntas comuns.
- Integração com a API da Wikipédia (pt-BR) para responder 'o que é', 'quem foi', 'onde fica', etc.
"""

import json
import random
import urllib.parse
import urllib.request
import unicodedata

# ---------------------------------------------------------------------------
# Banco de Curiosidades Curadas
# ---------------------------------------------------------------------------

CURIOSIDADES = [
    "Você sabia que o coração de uma baleia-azul é do tamanho de um carro Fusca e bate apenas 9 vezes por minuto?",
    "Sabia que a Via Láctea tem mais de 100 bilhões de estrelas, mas existem mais árvores na Terra do que estrelas na nossa galáxia? São cerca de 3 trilhões de árvores!",
    "Sabia que o mel nunca estraga? Arqueólogos já encontraram potes de mel em tumbas egípcias com mais de 3.000 anos que ainda estavam perfeitamente comestíveis!",
    "Você sabia que Vênus é o único planeta do nosso sistema solar que gira no sentido horário?",
    "Sabia que o polvo tem três corações e o sangue dele é azul devido à presença de cobre?",
    "Sabia que um dia em Vênus é mais longo do que um ano inteiro em Vênus? Ele demora 243 dias terrestres para girar sobre seu próprio eixo!",
    "Você sabia que os tubarões são mais antigos do que as árvores e os anéis de Saturno?",
    "Sabia que o lugar mais frio do universo conhecido fica na Terra? É o laboratório de átomos frios da NASA na Estação Espacial Internacional!",
    "Você sabia que os gatos passam cerca de 70% da vida dormindo?",
    "Sabia que a água quente congela mais rápido que a água fria em certas condições? Isso se chama Efeito Mpemba!",
    "Você sabia que as bananas são levemente radioativas porque são ricas em potássio?",
    "Sabia que a Torre Eiffel pode ser até 15 centímetros mais alta durante o verão por causa da dilatação térmica do ferro?",
    "Você sabia que o cérebro humano gera energia suficiente para acender uma lâmpada LED fraca?",
    "Sabia que as nuvens parecem leves, mas uma nuvem de tempestade média pode pesar mais de 500 toneladas?",
    "Você sabia que a borboleta sente o gosto dos alimentos usando as patas?",
]

# ---------------------------------------------------------------------------
# Respostas Diretas / Rápidas
# ---------------------------------------------------------------------------

RESPOSTAS_RAPIDAS = {
    "quem criou voce": "Eu fui criado para ser o seu assistente virtual pessoal estilo JARVIS!",
    "quem e voce": "Eu sou o JARVIS, seu assistente pessoal virtual!",
    "qual seu nome": "Meu nome é JARVIS!",
    "qual e a velocidade da luz": "A velocidade da luz no vácuo é de aproximadamente 300 mil quilômetros por segundo!",
    "qual o maior planeta": "O maior planeta do Sistema Solar é Júpiter!",
    "qual o maior oceano": "O Oceano Pacífico é o maior e mais profundo oceano da Terra!",
    "qual a capital do brasil": "A capital do Brasil é Brasília!",
    "o que e ia": "Inteligência Artificial é a capacidade de máquinas e sistemas computacionais simularem o raciocínio humano para aprender e resolver problemas!",
}


def _normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().strip()


def obter_curiosidade() -> str:
    """Retorna uma curiosidade aleatória do banco."""
    return random.choice(CURIOSIDADES)


def buscar_resposta_wikipedia(termo: str) -> str | None:
    """
    Busca o resumo da Wikipédia em português via API REST oficial.
    Retorna 1 ou 2 frases curtas com a explicação ou None se não encontrar.
    """
    if not termo:
        return None

    try:
        termo_encoded = urllib.parse.quote(termo)
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{termo_encoded}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "JarvisVirtualAssistant/1.0 (python-urllib)"}
        )

        with urllib.request.urlopen(req, timeout=3.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                extract = data.get("extract")
                if extract and len(extract) > 20:
                    # Limita a resposta para 2 frases para ser agradável de ouvir
                    frases = extract.split(". ")
                    resumo = ". ".join(frases[:2]).strip()
                    if not resumo.endswith("."):
                        resumo += "."
                    return resumo
    except Exception as e:
        print(f"[conhecimento] Consulta Wikipédia falhou: {e}")

    return None


def responder_pergunta(texto: str) -> str | None:
    """
    Tenta responder a uma pergunta geral usando respostas rápidas ou a Wikipédia.
    """
    norm = _normalizar(texto)

    # 1. Checa respostas rápidas
    for chave, resp in RESPOSTAS_RAPIDAS.items():
        if chave in norm:
            return resp

    # 2. Extrai o termo principal de perguntas comuns
    prefixos = [
        "o que e um ", "o que e uma ", "o que e o ", "o que e a ", "o que e ",
        "o que significa ", "quem foi ", "quem e ", "onde fica ",
        "como funciona ", "me explica ", "fala sobre ", "sabe o que e ",
        "qual o significado de ", "significado de ",
    ]

    termo_busca = None
    for p in prefixos:
        if norm.startswith(p):
            termo_busca = norm[len(p):].strip()
            break

    if not termo_busca and ("o que e" in norm or "quem foi" in norm or "quem e" in norm):
        for p in ["o que e", "quem foi", "quem e"]:
            if p in norm:
                termo_busca = norm.split(p)[-1].strip()
                break

    if termo_busca:
        resumo = buscar_resposta_wikipedia(termo_busca)
        if resumo:
            return f"Olha o que eu sei sobre isso: {resumo}"

    return None
