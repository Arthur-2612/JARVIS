"""
JARVIS — Assistente pessoal com voz, interface HUD e entrada manual.

Fluxo v3 (modo contínuo + anti-eco):
  1. Abre a interface HUD premium.
  2. Calibra o microfone (2 s de ruído ambiente).
  3. Fala uma saudação.
  4. Loop contínuo: ouve o microfone sem precisar chamar pelo nome.
     IMPORTANTE: o microfone fica mudo enquanto o JARVIS está falando
     (voz.falando Event) — ele não ouve a própria voz.
  5. Campo de texto sempre disponível como fallback.
  6. Botão 'Detectar Microfone' na GUI permite trocar o device em tempo real.
"""

import json
import threading
import time
from pathlib import Path

from core import acoes, cerebro, ouvido, voz
from core.diagnostico import listar_microfones, salvar_device_index
from core.palmas import DetectorDePalmas
from gui.interface import InterfaceJarvis

CONFIG_PATH = Path(__file__).parent / "config.json"


def carregar_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class Jarvis:
    def __init__(self):
        self.config     = carregar_config()
        self.pausado    = False
        self.encerrando = False

        # Cria a interface passando callbacks para detecção de microfone
        self.interface = InterfaceJarvis(
            on_comando_manual      = self.processar_texto_manual,
            on_fechar              = self.encerrar,
            on_detectar_microfones = self._obter_microfones,
            on_salvar_microfone    = self._salvar_microfone,
        )

        # Detector de palmas (opcional)
        self.detector_palmas = None
        if self.config.get("comportamento", {}).get("usar_palmas_como_gatilho_alternativo", False):
            self.detector_palmas = DetectorDePalmas(on_duas_palmas=self.alternar_pausa)

    # ── Callbacks de microfone ───────────────────────────────────────────────

    def _obter_microfones(self) -> list[tuple[int, str]]:
        return listar_microfones()

    def _salvar_microfone(self, device_index):
        self.config.setdefault("microfone", {})["device_index"] = device_index
        salvar_device_index(CONFIG_PATH, device_index)
        # Recalibra com o novo dispositivo
        threading.Thread(
            target=self._recalibrar, args=(device_index,), daemon=True
        ).start()

    def _recalibrar(self, device_index=None):
        self.interface.registrar_log("[sistema] Recalibrando microfone...", "sistema")
        ouvido.calibrar_microfone(device_index=device_index, duration=2.0)
        self.interface.registrar_log("[sistema] Calibração concluída.", "sistema")

    # ── Ciclo de vida ────────────────────────────────────────────────────────

    def iniciar(self):
        thread_voz = threading.Thread(target=self._loop_de_voz, daemon=True)
        thread_voz.start()

        if self.detector_palmas:
            try:
                self.detector_palmas.iniciar()
            except Exception as e:
                print(f"[main] Detector de palmas não pôde iniciar: {e}")

        self.interface.rodar()   # bloqueia (Tkinter precisa da thread principal)

    def encerrar(self):
        self.encerrando = True
        if self.detector_palmas:
            self.detector_palmas.parar()

    def alternar_pausa(self):
        self.pausado = not self.pausado
        estado = "PAUSADO" if self.pausado else "OUVINDO..."
        self.interface.registrar_log(
            f"[sistema] Assistente {'pausado' if self.pausado else 'retomado'}.",
            "sistema",
        )
        self.interface.atualizar_status(estado)

    # ── Loop principal de voz (modo contínuo) ────────────────────────────────

    def _loop_de_voz(self):
        comportamento = self.config.get("comportamento", {})
        saudacao = comportamento.get("saudacao_ao_iniciar", "E aí! Jarvis online. Tô aqui pra te ajudar no que precisar!")
        idioma   = self.config.get("idioma_reconhecimento", "pt-BR")
        timeout  = comportamento.get("tempo_limite_escuta_segundos", 5)
        limite   = comportamento.get("tempo_limite_frase_segundos", 10)

        # Exibe nome do microfone inicial
        device_index = self.config.get("microfone", {}).get("device_index")
        mics = listar_microfones()
        if device_index is not None and mics:
            nome = next((n for i, n in mics if i == device_index), f"device {device_index}")
        else:
            nome = "Padrão do sistema"
        self.interface.atualizar_microfone(nome)

        # Calibração inicial
        self.interface.atualizar_status("CALIBRANDO...")
        self.interface.registrar_log("[sistema] Calibrando microfone (2 s)...", "sistema")
        ouvido.calibrar_microfone(device_index=device_index, duration=2.0)
        self.interface.registrar_log("[sistema] Calibração concluída.", "sistema")

        # Saudação
        self._falar(saudacao)
        self.interface.atualizar_status("OUVINDO...")

        while not self.encerrando:
            if self.pausado:
                time.sleep(0.2)
                continue

            # ── Aguarda o JARVIS terminar de falar (anti-eco) ────────────
            if voz.falando.is_set():
                voz.falando.wait()   # bloqueia até `falando` ser limpo
                time.sleep(0.3)      # pausa extra pós-fala
                continue

            def _on_status(s):
                mapa = {
                    "ouvindo":      "OUVINDO...",
                    "processando":  "PROCESSANDO...",
                    "silencio":     "OUVINDO...",
                    "erro":         "ERRO DE ÁUDIO",
                }
                self.interface.atualizar_status(mapa.get(s, s.upper()))

            texto = ouvido.ouvir_comando(
                idioma=idioma,
                timeout=timeout,
                phrase_time_limit=limite,
                config=self.config,
                on_status=_on_status,
            )

            if not texto or self.pausado or self.encerrando:
                continue

            # Recusa captura se o JARVIS acabou de falar (eco residual)
            if voz.falando.is_set():
                continue

            self.interface.registrar_log(f"Você (voz): {texto}", "voz")
            self.interface.atualizar_status("PROCESSANDO...")
            self._executar(texto)

            if not self.encerrando:
                self.interface.atualizar_status("OUVINDO...")

    # ── Entrada manual ───────────────────────────────────────────────────────

    def processar_texto_manual(self, texto: str):
        threading.Thread(target=self._executar, args=(texto,), daemon=True).start()

    # ── Núcleo comum de execução ─────────────────────────────────────────────

    def _executar(self, texto: str):
        resposta = cerebro.processar_comando(texto, self.config)

        if resposta == "__SAIR__":
            self._falar("Beleza! Encerrando por aqui. Qualquer coisa é só chamar!")
            self.encerrar()
            self.interface.root.after(800, self.interface.root.destroy)
            return

        if resposta == "__PAUSAR__":
            self.pausado = True
            self._falar("Tá bom, vou ficar quieto por um tempo. Fala quando precisar!")
            self.interface.atualizar_status("PAUSADO")
            return

        # Resposta vazia = ruído filtrado pelo cérebro, não faz nada
        if not resposta:
            return

        self._falar(resposta)

    def _falar(self, texto: str):
        voz.falar(
            texto,
            self.config.get("voz", {}),
            callback_texto=lambda t: self.interface.registrar_log(t, "jarvis"),
        )


if __name__ == "__main__":
    Jarvis().iniciar()
