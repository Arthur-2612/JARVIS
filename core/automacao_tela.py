"""
Módulo de Visão e Automação de Tela do JARVIS.

Permite que o JARVIS:
- Tire screenshots e analise a janela ativa.
- Feche janelas/abas, minimize telas e alterne aplicativos.
- Digite textos perfeitamente (com suporte a acentuação em PT-BR).
- Realize comandos de teclado (copiar, colar, selecionar tudo, scroll).
"""

import os
import time
import ctypes
from datetime import datetime

try:
    import pyautogui
    # Configuração de segurança do PyAutoGUI
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.2
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

# Pasta para salvar capturas de tela
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "screenshots")


def _garantir_diretorio_screenshots():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def obter_titulo_janela_ativa() -> str:
    """Retorna o título da janela atualmente em foco no Windows."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value.strip() or "Área de Trabalho ou Sistema"
    except Exception:
        return "Janela desconhecida"


def capturar_tela() -> str:
    """Captura a tela inteira e salva em assets/screenshots."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor Faria. A biblioteca PyAutoGUI não está instalada para captura de tela."

    try:
        _garantir_diretorio_screenshots()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"print_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)

        pyautogui.screenshot(filepath)
        janela = obter_titulo_janela_ativa()
        return f"Captura de tela realizada com sucesso, Senhor Faria! Imagem salva em seus arquivos. Janela ativa identificada: '{janela}'."
    except Exception as e:
        return f"Desculpe, Senhor Faria. Ocorreu uma falha ao capturar a tela: {e}"


def analisar_visao_tela() -> str:
    """Relata o estado atual da tela, resolução e aplicativo ativo."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. O módulo de visão local necessita das bibliotecas de automação."

    try:
        largura, altura = pyautogui.size()
        janela_ativa = obter_titulo_janela_ativa()
        pos_x, pos_y = pyautogui.position()

        return (
            f"Visão de tela ativada, Senhor Faria. "
            f"Resolução atual: {largura} por {altura} pixels. "
            f"Aplicativo em foco no momento: '{janela_ativa}'. "
            f"Cursor do mouse posicionado em ({pos_x}, {pos_y})."
        )
    except Exception as e:
        return f"Erro ao analisar o status visual da tela, Senhor: {e}"


def fechar_janela() -> str:
    """Fecha a janela ou programa em foco (Alt+F4)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        janela = obter_titulo_janela_ativa()
        pyautogui.hotkey('alt', 'f4')
        return f"Fechando a janela '{janela}', Senhor Faria."
    except Exception as e:
        return f"Falha ao fechar a janela, Senhor: {e}"


def fechar_aba() -> str:
    """Fecha a aba atual do navegador ou leitor (Ctrl+W)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('ctrl', 'w')
        return "Aba encerrada com sucesso, Senhor Faria."
    except Exception as e:
        return f"Falha ao fechar aba, Senhor: {e}"


def minimizar_janela() -> str:
    """Minimiza a janela ativa (Win + Seta para Baixo)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('win', 'down')
        time.sleep(0.1)
        pyautogui.hotkey('win', 'down')
        return "Janela minimizada, Senhor Faria."
    except Exception as e:
        return f"Não foi possível minimizar a janela, Senhor: {e}"


def minimizar_tudo() -> str:
    """Minimiza todas as janelas e exibe a Área de Trabalho (Win + D)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('win', 'd')
        return "Todas as janelas foram minimizadas, Senhor Faria. Área de trabalho visível."
    except Exception as e:
        return f"Falha ao minimizar todas as telas, Senhor: {e}"


def maximizar_janela() -> str:
    """Maximiza a janela ativa (Win + Seta para Cima)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('win', 'up')
        return "Janela maximizada, Senhor Faria."
    except Exception as e:
        return f"Falha ao maximizar janela, Senhor: {e}"


def alternar_janela() -> str:
    """Alterna para o próximo aplicativo aberto (Alt + Tab)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('alt', 'tab')
        janela = obter_titulo_janela_ativa()
        return f"Alternado para a janela: '{janela}', Senhor Faria."
    except Exception as e:
        return f"Falha ao alternar janela, Senhor: {e}"


def escrever_texto(texto: str) -> str:
    """
    Digita o texto no campo ativo. Usa a área de transferência (pyperclip)
    para garantir suporte perfeito a acentos e caracteres especiais.
    """
    if not texto:
        return "Senhor Faria, nenhum texto foi informado para digitação."

    try:
        if HAS_PYPERCLIP:
            conteudo_anterior = pyperclip.paste()
            pyperclip.copy(texto)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            # Tenta restaurar a área de transferência anterior após a digitação
            try:
                pyperclip.copy(conteudo_anterior)
            except Exception:
                pass
        else:
            pyautogui.write(texto, interval=0.03)

        return f"Texto digitado no aplicativo em foco, Senhor Faria."
    except Exception as e:
        return f"Falha ao digitar o texto solicitado, Senhor: {e}"


def copiar() -> str:
    """Copia a seleção atual (Ctrl + C)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('ctrl', 'c')
        return "Conteúdo copiado para a área de transferência, Senhor Faria."
    except Exception as e:
        return f"Erro ao copiar, Senhor: {e}"


def colar() -> str:
    """Cola o conteúdo da área de transferência (Ctrl + V)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('ctrl', 'v')
        return "Conteúdo colado com sucesso, Senhor Faria."
    except Exception as e:
        return f"Erro ao colar, Senhor: {e}"


def selecionar_tudo() -> str:
    """Seleciona todo o texto/conteúdo da janela ativa (Ctrl + A)."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        pyautogui.hotkey('ctrl', 'a')
        return "Todo o conteúdo foi selecionado, Senhor Faria."
    except Exception as e:
        return f"Erro ao selecionar tudo, Senhor: {e}"


def rolar_tela(direcao: str = "baixo") -> str:
    """Rola a página/tela para cima ou para baixo."""
    if not HAS_PYAUTOGUI:
        return "Lamento, Senhor. PyAutoGUI indisponível."
    try:
        clicks = -500 if direcao == "baixo" else 500
        pyautogui.scroll(clicks)
        return f"Página rolada para {direcao}, Senhor Faria."
    except Exception as e:
        return f"Erro ao rolar a tela, Senhor: {e}"
