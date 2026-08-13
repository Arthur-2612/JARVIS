"""
JARVIS - assistente pessoal com voz, interface HUD e entrada manual.

Fluxo:
  1. Abre a interface (HUD).
  2. Fala uma saudação.
  3. Fica em loop ouvindo o microfone. Quando reconhece um comando,
     interpreta (core/cerebro.py) e executa a ação (core/acoes.py).
  4. Em paralelo, um detector de duas palmas permite pausar/retomar
     a escuta sem precisar falar.
  5. A qualquer momento você também pode digitar o comando na caixa
     de texto da interface — é o caminho manual, sempre disponível,
     para nunca depender 100% do reconhecimento de voz.
"""

import json
import threading
import time
from pathlib import Path

from core import acoes, cerebro, ouvido, voz
from core.palmas import DetectorDePalmas
from gui.interface import InterfaceJarvis

CONFIG_PATH = Path(__file__).parent / "config.json"


def carregar_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class Jarvis:
    def __init__(self):
        self.config = carregar_config()
        self.pausado = False
        self.encerrando = False

        self.interface = InterfaceJarvis(
            on_comando_manual=self.processar_texto_manual,
            on_fechar=self.encerrar,
        )

        self.detector_palmas = None
        if self.config.get("comportamento", {}).get("usar_palmas_como_gatilho_alternativo", False):
            self.detector_palmas = DetectorDePalmas(on_duas_palmas=self.alternar_pausa)

    def _tem_ativacao_por_voz(self, texto: str) -> bool:
        if not texto:
            return False

        texto = texto.lower().strip()
        palavras_ativacao = self.config.get("comportamento", {}).get(
            "palavras_ativacao",
            ["jarvis", "oi jarvis", "olá jarvis"]
        )
        return any(palavra in texto for palavra in palavras_ativacao)

    def _remover_ativacao_por_voz(self, texto: str) -> str:
        texto = texto.lower().strip()
        palavras_ativacao = sorted(
            self.config.get("comportamento", {}).get("palavras_ativacao", ["jarvis"]),
            key=len,
            reverse=True,
        )

        for palavra in palavras_ativacao:
            if palavra in texto:
                texto = texto.replace(palavra, "", 1).strip(" ,;:-._")
                break
        return texto

    # ---------- ciclo de vida ----------

    def iniciar(self):
        thread_voz = threading.Thread(target=self._loop_de_voz, daemon=True)
        thread_voz.start()

        if self.detector_palmas:
            try:
                self.detector_palmas.iniciar()
            except Exception as e:
                print(f"[main] Detector de palmas não pôde iniciar (sem microfone disponível?): {e}")

        self.interface.rodar()  # bloqueia a thread principal (Tkinter precisa disso)

    def encerrar(self):
        self.encerrando = True
        if self.detector_palmas:
            self.detector_palmas.parar()

    def alternar_pausa(self):
        self.pausado = not self.pausado
        estado = "pausado (duas palmas)" if self.pausado else "retomado (duas palmas)"
        self.interface.registrar_log(f"[sistema] Assistente {estado}.")
        self.interface.atualizar_status("PAUSADO" if self.pausado else "OUVINDO...")

    # ---------- loop principal de voz ----------

    def _loop_de_voz(self):
        comportamento = self.config.get("comportamento", {})
        saudacao = comportamento.get("saudacao_ao_iniciar", "Sistemas online.")
        self._falar(saudacao)
        self.interface.atualizar_status("OUVINDO...")

        idioma = self.config.get("idioma_reconhecimento", "pt-BR")
        timeout = comportamento.get("tempo_limite_escuta_segundos", 6)
        limite_frase = comportamento.get("tempo_limite_frase_segundos", 7)

        while not self.encerrando:
            if self.pausado:
                time.sleep(0.2)
                continue

            texto = ouvido.ouvir_comando(
                idioma=idioma,
                timeout=timeout,
                phrase_time_limit=limite_frase,
                config=self.config,
            )
            if not texto or self.pausado or self.encerrando:
                continue

            if self.config.get("comportamento", {}).get("usar_ativacao_por_palavra", True):
                if not self._tem_ativacao_por_voz(texto):
                    continue
                texto = self._remover_ativacao_por_voz(texto)
                if not texto:
                    continue

            self.interface.registrar_log(f"Você (voz): {texto}")
            self.interface.atualizar_status("PROCESSANDO...")
            self._executar(texto)
            if not self.encerrando:
                self.interface.atualizar_status("PAUSADO" if self.pausado else "OUVINDO...")

    # ---------- entrada manual (caixa de texto da interface) ----------

    def processar_texto_manual(self, texto: str):
        threading.Thread(target=self._executar, args=(texto,), daemon=True).start()

    # ---------- núcleo comum de execução ----------

    def _executar(self, texto: str):
        resposta = cerebro.processar_comando(texto, self.config)

        if resposta == "__SAIR__":
            self._falar("Encerrando. Até logo, senhor.")
            self.encerrar()
            self.interface.root.after(500, self.interface.root.destroy)
            return

        if resposta == "__PAUSAR__":
            self.pausado = True
            self._falar("Entendido. Vou pausar a escuta por voz. Bata duas palmas para eu voltar.")
            self.interface.atualizar_status("PAUSADO")
            return

        self._falar(resposta)

    def _falar(self, texto: str):
        voz.falar(texto, self.config.get("voz", {}), callback_texto=self.interface.registrar_log)


if __name__ == "__main__":
    Jarvis().iniciar()
