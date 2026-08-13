"""
Interface HUD do JARVIS: círculo estilo arc-reactor com anéis girando,
área de status, log de conversa e uma caixa de texto para digitar
comandos manualmente (fallback para quando voz não é prática ou falha).
"""

import queue
import tkinter as tk
from tkinter import scrolledtext
import math

COR_FUNDO = "#050708"
COR_ANEL = "#33d9e8"
COR_ANEL_FRACO = "#134b52"
COR_TEXTO = "#66f2ff"
COR_TEXTO_STATUS = "#8fdfe8"


class InterfaceJarvis:
    def __init__(self, on_comando_manual, on_fechar):
        self.on_comando_manual = on_comando_manual
        self.on_fechar = on_fechar

        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S")
        self.root.configure(bg=COR_FUNDO)
        self.root.geometry("620x760")
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self._fila_eventos = queue.Queue()
        self._angulo = 0

        self._montar_layout()
        self._animar_aneis()
        self.root.after(100, self._processar_fila)

    # ---------- layout ----------

    def _montar_layout(self):
        self.canvas = tk.Canvas(self.root, width=600, height=420, bg=COR_FUNDO, highlightthickness=0)
        self.canvas.pack(pady=(15, 5))

        self.label_status = tk.Label(
            self.root, text="INICIALIZANDO...", font=("Consolas", 13, "bold"),
            fg=COR_TEXTO_STATUS, bg=COR_FUNDO
        )
        self.label_status.pack(pady=(0, 10))

        self.log = scrolledtext.ScrolledText(
            self.root, height=14, bg="#0a0e10", fg=COR_TEXTO,
            insertbackground=COR_TEXTO, font=("Consolas", 10), bd=0
        )
        self.log.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.log.configure(state="disabled")

        frame_entrada = tk.Frame(self.root, bg=COR_FUNDO)
        frame_entrada.pack(fill="x", padx=15, pady=(0, 15))

        self.entrada = tk.Entry(
            frame_entrada, bg="#0a0e10", fg=COR_TEXTO, insertbackground=COR_TEXTO,
            font=("Consolas", 11), relief="flat"
        )
        self.entrada.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self.entrada.bind("<Return>", self._enviar_manual)

        botao = tk.Button(
            frame_entrada, text="ENVIAR", command=self._enviar_manual,
            bg=COR_ANEL, fg="#03181a", font=("Consolas", 10, "bold"),
            relief="flat", padx=12, cursor="hand2"
        )
        botao.pack(side="right")

    # ---------- animação do arc-reactor ----------

    def _desenhar_aneis(self):
        self.canvas.delete("all")
        cx, cy = 300, 210

        for raio, largura, cor, velocidade, tracejado in [
            (170, 3, COR_ANEL_FRACO, 0.4, (2, 6)),
            (140, 4, COR_ANEL, -0.7, (14, 10)),
            (110, 2, COR_ANEL_FRACO, 1.1, (3, 5)),
            (85, 3, COR_ANEL, -1.4, (10, 8)),
        ]:
            inicio = (self._angulo * velocidade) % 360
            self.canvas.create_arc(
                cx - raio, cy - raio, cx + raio, cy + raio,
                start=inicio, extent=300, style="arc",
                outline=cor, width=largura
            )

        self.canvas.create_text(
            cx, cy, text="J.A.R.V.I.S", fill=COR_TEXTO,
            font=("Consolas", 20, "bold")
        )

    def _animar_aneis(self):
        self._desenhar_aneis()
        self._angulo = (self._angulo + 1) % 360
        self.root.after(30, self._animar_aneis)

    # ---------- eventos vindos de outras threads ----------

    def _processar_fila(self):
        try:
            while True:
                tipo, valor = self._fila_eventos.get_nowait()
                if tipo == "status":
                    self.label_status.configure(text=valor)
                elif tipo == "log":
                    self._adicionar_log(valor)
        except queue.Empty:
            pass
        self.root.after(100, self._processar_fila)

    def _adicionar_log(self, texto: str):
        self.log.configure(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---------- API pública (thread-safe) ----------

    def atualizar_status(self, texto: str):
        self._fila_eventos.put(("status", texto))

    def registrar_log(self, texto: str):
        self._fila_eventos.put(("log", texto))

    # ---------- entrada manual ----------

    def _enviar_manual(self, event=None):
        texto = self.entrada.get().strip()
        if not texto:
            return
        self.entrada.delete(0, "end")
        self.registrar_log(f"Você (texto): {texto}")
        self.on_comando_manual(texto)

    def _ao_fechar(self):
        self.on_fechar()
        self.root.destroy()

    def rodar(self):
        self.root.mainloop()
