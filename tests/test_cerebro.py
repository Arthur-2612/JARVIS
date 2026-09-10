from core import cerebro


def test_normaliza_comando_remove_jarvis_e_pontuacao():
    assert cerebro.normalizar_texto("Jarvis, abre o Chrome!.") == "abre chrome"


def test_normaliza_comando_remove_acentos():
    assert cerebro.normalizar_texto("Que horas são?") == "que horas sao"


def test_palavra_chave_nao_aceita_trecho_de_palavra():
    assert not cerebro._tem_palavra("pesquisador", ["pesquisar"])


def test_processar_comando_abrir_app_com_variacao_natural():
    config = {
        "apps": {
            "chrome": {"type": "path", "value": "C:/Program Files/Google/Chrome/Application/chrome.exe"},
            "spotify": {"type": "path", "value": "C:/Spotify/Spotify.exe"},
        }
    }
    resposta = cerebro.processar_comando("jarvis abre o chrome", config)
    assert resposta.startswith("Abrindo chrome")


def test_processar_comando_pesquisa_com_variacao_natural():
    resposta = cerebro.processar_comando("jarvis, pesquise sobre python", {"apps": {}})
    assert "python" in resposta.lower()
    assert "google" in resposta.lower()


def test_processar_comando_sair():
    assert cerebro.processar_comando("encerrar jarvis", {"apps": {}}) == "__SAIR__"
