import json
from pathlib import Path


def test_configuracao_tem_secoes_principais():
    caminho = Path(__file__).parents[1] / "config.json"
    configuracao = json.loads(caminho.read_text(encoding="utf-8"))

    assert "idioma_reconhecimento" in configuracao
    assert "voz" in configuracao
    assert "comportamento" in configuracao
    assert "apps" in configuracao