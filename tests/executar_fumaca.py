import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from tests.test_config import test_configuracao_tem_secoes_principais
from tests.test_cerebro import (
    test_abrir_item_rejeita_configuracao_invalida,
    test_normaliza_comando_remove_acentos,
    test_normaliza_comando_remove_jarvis_e_pontuacao,
    test_palavra_chave_nao_aceita_trecho_de_palavra,
)


def main():
    testes = [
        test_configuracao_tem_secoes_principais,
        test_abrir_item_rejeita_configuracao_invalida,
        test_normaliza_comando_remove_acentos,
        test_normaliza_comando_remove_jarvis_e_pontuacao,
        test_palavra_chave_nao_aceita_trecho_de_palavra,
    ]
    for teste in testes:
        teste()
    print(f"{len(testes)} testes de fumaça passaram.")


if __name__ == "__main__":
    main()