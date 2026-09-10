# J.A.R.V.I.S — Assistente Pessoal

Assistente de voz local, com interface estilo arc-reactor, que abre
programas, pesquisa coisas e conversa com você por voz — com entrada
manual sempre disponível como plano B.

## Sobre a voz

Não é possível usar a voz original do filme (é a voz do ator Paul Bettany,
protegida por direitos autorais da Marvel/Disney). O projeto usa uma voz
neural gratuita da Microsoft (Edge TTS), grave e formal, configurada para
soar próxima ao estilo "assistente futurista". Você pode trocar a voz
facilmente em `config.json` → `"voz"` → `"voz_edge_tts"`. Algumas opções:

- `pt-BR-AntonioNeural` (padrão, masculino, grave)
- `en-GB-RyanNeural` (inglês britânico, tom mais "clássico de filme")
- Lista completa: rode `edge-tts --list-voices` no terminal depois de instalar.

## Estrutura de pastas

```
JARVIS/
├── main.py                              # ponto de entrada
├── config.json                          # apps, vozes, idioma, comportamento
├── requirements.txt
├── instalar_dependencias.bat            # instala tudo com um clique
├── instalar_inicializacao_automatica.ps1 # faz o JARVIS abrir sozinho no boot
├── core/
│   ├── ouvido.py     # reconhecimento de fala (STT)
│   ├── voz.py        # síntese de fala (TTS)
│   ├── cerebro.py    # interpreta o comando e decide a ação
│   ├── acoes.py      # abre apps, YouTube, pesquisa Google, diz as horas
│   └── palmas.py     # gatilho alternativo: duas palmas pausam/retomam
├── gui/
│   └── interface.py  # HUD com anéis animados + log + entrada manual
├── assets/           # (reservado para ícones/sons futuros)
└── logs/             # (reservado para logs futuros)
```

## 1. Instalar

```
instalar_dependencias.bat
```

Se o `PyAudio` falhar na instalação (comum no Windows), rode:

```
pip install pipwin
pipwin install pyaudio
```

## 2. Configurar seus aplicativos

Edite `config.json` → `"apps"`. Cada entrada é:

- `"type": "path"` + caminho completo do `.exe` (ex.: Chrome, Spotify)
- `"type": "command"` + comando do Windows (ex.: `notepad`, `calc`)
- `"type": "url"` + endereço que abre no navegador

**YouTube já vem com uma regra fixa**: qualquer comando que mencione
"youtube" abre sempre `https://www.youtube.com` de verdade (ou já com
busca, se você disser "abrir youtube e tocar [nome]").

## 3. Rodar

```
python main.py
```

A janela do HUD abre, ele fala a saudação e já fica ouvindo. Comandos que
funcionam de fábrica:

- "abrir chrome" / "abrir spotify" / "abrir bloco de notas" (qualquer app do config.json)
- "abrir youtube" / "abrir youtube e tocar [música]"
- "pesquisar [algo]" (busca no Google)
- "que horas são"
- "pausar" (para de ouvir até você bater duas palmas ou digitar de novo)
- "encerrar jarvis" (fecha o programa)

**Entrada manual**: a caixa de texto embaixo do log funciona a qualquer
momento — digite o comando e aperte Enter. É o caminho garantido para
quando o microfone falhar, tiver ruído demais, ou você simplesmente
preferir digitar.

**Duas palmas**: continuam funcionando como gatilho alternativo — pausam
e retomam a escuta por voz sem precisar falar nem digitar nada.

## 4. Abrir sozinho com o Windows

Clique com o botão direito em `instalar_inicializacao_automatica.ps1` →
"Executar com PowerShell". Isso cria um atalho na pasta de Inicialização
do Windows. Para desativar depois, é só apagar esse atalho (o script te
mostra o caminho exato dele).

## Limitações honestas

- O reconhecimento de voz (`recognize_google`) precisa de internet e usa
  a API gratuita do Google — para uso pessoal funciona bem, mas tem
  limite de uso e não é 100% preciso com sotaque/ruído forte.
- A voz é sintética (Edge TTS), não é gravação da voz do filme.
- A detecção de "qual app abrir" é por palavra-chave simples — funciona
  bem para comandos diretos, não é um LLM entendendo linguagem livre.
  Se quiser, dá pra evoluir isso depois para usar a API da Anthropic e
  interpretar comandos mais soltos — é só avisar que eu ajudo a integrar.
