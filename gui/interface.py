"""
Interface HUD Premium do JARVIS v2.

Design sci-fi de alta fidelidade com:
- Fundo com grade holográfica animada.
- Arc-reactor central com múltiplos anéis pulsantes e efeito glow.
- Anel externo que pulsa em azul/ciano quando OUVINDO.
- Badge de status animado com cores semânticas.
- Painel lateral de diagnóstico de microfone.
- Log de conversa com cores diferenciadas por falante.
- Campo de entrada estilizado com ícone de microfone.
- Botão flutuante para detectar/trocar microfone.
"""

import queue
import math
import threading
import tkinter as tk
from tkinter import font as tkfont
import time

# ── Paleta de cores ──────────────────────────────────────────────────────────
BG          = "#03070a"       # quase preto com leve tint azul
BG2         = "#060d12"       # levemente mais claro para painéis
CYAN        = "#00e5ff"       # ciano principal
CYAN_DIM    = "#00617a"       # ciano escuro
CYAN_GLOW   = "#4dfff3"       # ciano brilhante para glow
GOLD        = "#ffd54f"       # dourado para alertas/tempo
GREEN       = "#00e676"       # verde status OK
RED         = "#ff1744"       # vermelho erro/pausado
ORANGE      = "#ff9100"       # laranja processando
WHITE       = "#e0f7fa"       # texto principal
GRAY        = "#37474f"       # texto secundário
PANEL_BG    = "#080f14"       # fundo do painel de log

# ── Fontes ───────────────────────────────────────────────────────────────────
FONT_TITLE   = ("Consolas", 18, "bold")
FONT_STATUS  = ("Consolas", 11, "bold")
FONT_LOG     = ("Consolas",  9)
FONT_INPUT   = ("Consolas", 10)
FONT_SMALL   = ("Consolas",  8)
FONT_MIC     = ("Consolas",  9, "bold")

# ── Tamanho da janela ────────────────────────────────────────────────────────
WIN_W, WIN_H = 680, 820
CX,    CY    = 340, 230   # centro do canvas do arc-reactor


class InterfaceJarvis:
    def __init__(self, on_comando_manual, on_fechar, on_detectar_microfones=None, on_salvar_microfone=None):
        self.on_comando_manual       = on_comando_manual
        self.on_fechar               = on_fechar
        self.on_detectar_microfones  = on_detectar_microfones   # callback → lista[(idx,nome)]
        self.on_salvar_microfone     = on_salvar_microfone      # callback(int|None)

        self._fila   = queue.Queue()
        self._angulo = 0.0
        self._status = "INICIALIZANDO"
        self._pulso  = 0.0          # 0..1, para anel pulsante
        self._pulso_dir = 1
        self._grade_offset = 0      # offset da grade holográfica

        self._microfone_atual = "Detectando..."
        self._mics_disponiveis: list[tuple[int, str]] = []

        self._construir_janela()
        self._construir_canvas()
        self._construir_status_badge()
        self._construir_log()
        self._construir_mic_panel()
        self._construir_entrada()

        self._animar()
        self.root.after(80, self._processar_fila)

    # ── Construção da janela ─────────────────────────────────────────────────

    def _construir_janela(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S — Sistema Online")
        self.root.configure(bg=BG)
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        # Tenta deixar sem borda nativa (visual mais limpo)
        try:
            self.root.overrideredirect(False)
        except Exception:
            pass

    # ── Canvas do arc-reactor ────────────────────────────────────────────────

    def _construir_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=WIN_W, height=460,
            bg=BG, highlightthickness=0,
        )
        self.canvas.pack(side="top", fill="x")

    # ── Badge de status ──────────────────────────────────────────────────────

    def _construir_status_badge(self):
        self.frame_status = tk.Frame(self.root, bg=BG)
        self.frame_status.pack(fill="x", padx=20, pady=(0, 6))

        self.label_status_dot = tk.Label(
            self.frame_status, text="●", font=("Consolas", 14),
            fg=GREEN, bg=BG,
        )
        self.label_status_dot.pack(side="left", padx=(0, 6))

        self.label_status = tk.Label(
            self.frame_status, text="INICIALIZANDO...",
            font=FONT_STATUS, fg=CYAN, bg=BG,
        )
        self.label_status.pack(side="left")

        # Separador horizontal
        sep = tk.Frame(self.root, height=1, bg=CYAN_DIM)
        sep.pack(fill="x", padx=12, pady=(0, 8))

    # ── Log de conversa ──────────────────────────────────────────────────────

    def _construir_log(self):
        frame_log = tk.Frame(self.root, bg=BG2, bd=0)
        frame_log.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # Cabeçalho do painel
        tk.Label(
            frame_log, text="◈  REGISTRO DE COMUNICAÇÃO",
            font=FONT_SMALL, fg=CYAN_DIM, bg=BG2, anchor="w",
        ).pack(fill="x", padx=8, pady=(6, 2))

        self.log = tk.Text(
            frame_log, bg=PANEL_BG, fg=WHITE,
            insertbackground=CYAN, font=FONT_LOG,
            bd=0, wrap="word", state="disabled",
            selectbackground=CYAN_DIM,
        )
        scroll = tk.Scrollbar(frame_log, command=self.log.yview, bg=BG2,
                               troughcolor=BG2, bd=0)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", pady=4, padx=(0, 4))
        self.log.pack(fill="both", expand=True, padx=(8, 0), pady=(0, 6))

        # Tags de cor por tipo de mensagem
        self.log.tag_configure("voz",    foreground=CYAN_GLOW, font=FONT_LOG + ("bold",) if False else FONT_LOG)
        self.log.tag_configure("jarvis", foreground=GOLD)
        self.log.tag_configure("sistema",foreground=GRAY)
        self.log.tag_configure("erro",   foreground=RED)
        self.log.tag_configure("texto",  foreground=GREEN)
        self.log.tag_configure("ts",     foreground=CYAN_DIM)

    # ── Painel de microfone ──────────────────────────────────────────────────

    def _construir_mic_panel(self):
        self.frame_mic = tk.Frame(self.root, bg=BG2, bd=0)
        self.frame_mic.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(
            self.frame_mic, text="◈  MICROFONE",
            font=FONT_SMALL, fg=CYAN_DIM, bg=BG2, anchor="w",
        ).pack(side="left", padx=8, pady=6)

        self.label_mic_nome = tk.Label(
            self.frame_mic, text="—",
            font=FONT_MIC, fg=WHITE, bg=BG2, anchor="w",
        )
        self.label_mic_nome.pack(side="left", padx=6, pady=6, fill="x", expand=True)

        btn_detectar = tk.Button(
            self.frame_mic, text="⟳ DETECTAR",
            command=self._abrir_dialogo_microfone,
            bg=CYAN_DIM, fg=CYAN, font=FONT_SMALL,
            relief="flat", padx=8, pady=3, cursor="hand2",
            activebackground=CYAN, activeforeground=BG,
        )
        btn_detectar.pack(side="right", padx=8, pady=4)

    # ── Campo de entrada de texto ────────────────────────────────────────────

    def _construir_entrada(self):
        frame_entrada = tk.Frame(self.root, bg=BG2, bd=0)
        frame_entrada.pack(fill="x", padx=12, pady=(0, 12))

        tk.Label(
            frame_entrada, text="▶",
            font=("Consolas", 12), fg=CYAN, bg=BG2,
        ).pack(side="left", padx=(10, 4), pady=8)

        self.entrada = tk.Entry(
            frame_entrada, bg=PANEL_BG, fg=WHITE,
            insertbackground=CYAN, font=FONT_INPUT,
            relief="flat", bd=0,
        )
        self.entrada.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 6))
        self.entrada.bind("<Return>", self._enviar_manual)
        self.entrada.insert(0, "Digite um comando ou fale...")
        self.entrada.configure(fg=GRAY)
        self.entrada.bind("<FocusIn>",  self._limpar_placeholder)
        self.entrada.bind("<FocusOut>", self._restaurar_placeholder)

        btn = tk.Button(
            frame_entrada, text="ENVIAR",
            command=self._enviar_manual,
            bg=CYAN, fg=BG, font=("Consolas", 10, "bold"),
            relief="flat", padx=14, pady=6, cursor="hand2",
            activebackground=CYAN_GLOW, activeforeground=BG,
        )
        btn.pack(side="right", padx=(0, 8), pady=4)

    # ── Animação principal ───────────────────────────────────────────────────

    def _animar(self):
        self._angulo = (self._angulo + 1.2) % 360
        self._pulso  += 0.04 * self._pulso_dir
        if self._pulso >= 1.0:
            self._pulso_dir = -1
        elif self._pulso <= 0.0:
            self._pulso_dir = 1
        self._grade_offset = (self._grade_offset + 0.4) % 40

        self._desenhar_cena()
        self.root.after(30, self._animar)

    def _cor_status(self):
        s = self._status
        if "OUVINDO" in s:
            return CYAN
        if "PROCESSANDO" in s:
            return ORANGE
        if "PAUSADO" in s or "PARADO" in s:
            return RED
        if "ERRO" in s:
            return RED
        return CYAN_DIM

    def _desenhar_cena(self):
        self.canvas.delete("all")
        self._desenhar_grade()
        self._desenhar_arc_reactor()
        self._desenhar_titulo()
        self._desenhar_varredura_lateral()

    # Grade holográfica de fundo
    def _desenhar_grade(self):
        off = self._grade_offset
        cor = "#0a1a22"
        for x in range(-40, WIN_W + 40, 40):
            self.canvas.create_line(x + off, 0, x + off, 460, fill=cor, width=1)
        for y in range(0, 461, 40):
            self.canvas.create_line(0, y + off, WIN_W, y + off, fill=cor, width=1)

    # Arc-reactor central
    def _desenhar_arc_reactor(self):
        status_cor = self._cor_status()

        # Anel de pulso externo (quando ouvindo)
        if "OUVINDO" in self._status:
            raio_pulso = 185 + 12 * self._pulso
            alpha_hex  = format(int(60 + 80 * self._pulso), "02x")
            cor_pulso  = CYAN  # tkinter Canvas não suporta alpha real, usamos tamanho
            self.canvas.create_oval(
                CX - raio_pulso, CY - raio_pulso,
                CX + raio_pulso, CY + raio_pulso,
                outline=CYAN_DIM, width=2 + int(2 * self._pulso),
            )
            self.canvas.create_oval(
                CX - raio_pulso + 10, CY - raio_pulso + 10,
                CX + raio_pulso - 10, CY + raio_pulso - 10,
                outline=CYAN, width=1,
            )

        # Anéis interiores
        aneis = [
            (170, 2, CYAN_DIM,  0.30, 280),
            (148, 3, status_cor, -0.60, 300),
            (122, 2, CYAN_DIM,  0.90, 260),
            (100, 3, status_cor, -1.20, 310),
            (78,  2, CYAN_DIM,  1.50, 270),
        ]
        for raio, larg, cor, vel, extent in aneis:
            inicio = (self._angulo * vel) % 360
            self.canvas.create_arc(
                CX - raio, CY - raio, CX + raio, CY + raio,
                start=inicio, extent=extent,
                style="arc", outline=cor, width=larg,
            )

        # Núcleo hexagonal (simulado com círculos concêntricos)
        for r, cor in [(54, "#0d2a35"), (44, "#0f3040"), (34, "#124050"), (22, CYAN_DIM)]:
            self.canvas.create_oval(
                CX - r, CY - r, CX + r, CY + r,
                fill=cor, outline="", width=0,
            )

        # Brilho central
        brilho = int(150 + 105 * self._pulso)
        hex_brilho = format(brilho, "02x")
        self.canvas.create_oval(
            CX - 14, CY - 14, CX + 14, CY + 14,
            fill=CYAN if "OUVINDO" in self._status else CYAN_DIM,
            outline=CYAN_GLOW, width=2,
        )

        # Linhas de varredura do núcleo
        for i in range(6):
            ang = math.radians(self._angulo * 0.5 + i * 60)
            x2  = CX + 50 * math.cos(ang)
            y2  = CY + 50 * math.sin(ang)
            self.canvas.create_line(CX, CY, x2, y2, fill=CYAN_DIM, width=1)

    # Título com sublinhado decorativo
    def _desenhar_titulo(self):
        self.canvas.create_text(
            CX, CY + 2, text="J.A.R.V.I.S",
            fill=CYAN_GLOW, font=("Consolas", 19, "bold"),
        )
        # Linha inferior decorativa
        self.canvas.create_line(CX - 55, CY + 14, CX + 55, CY + 14,
                                 fill=CYAN_DIM, width=1)

        # Versão / subtítulo
        self.canvas.create_text(
            CX, CY + 24, text="SISTEMA DE ASSISTÊNCIA PESSOAL v2",
            fill=CYAN_DIM, font=("Consolas", 7),
        )

        # Cantos decorativos do canvas
        for (x1, y1, x2, y2) in [
            (10, 10, 40, 10), (10, 10, 10, 40),
            (WIN_W-40, 10, WIN_W-10, 10), (WIN_W-10, 10, WIN_W-10, 40),
            (10, 450, 40, 450), (10, 410, 10, 450),
            (WIN_W-40, 450, WIN_W-10, 450), (WIN_W-10, 410, WIN_W-10, 450),
        ]:
            self.canvas.create_line(x1, y1, x2, y2, fill=CYAN_DIM, width=2)

    # Barras de varredura laterais (estilo HUD)
    def _desenhar_varredura_lateral(self):
        status_cor = self._cor_status()
        # Esquerda
        for i, (r, c) in enumerate([
            (1.0, CYAN_DIM), (0.85, CYAN_DIM), (0.7, CYAN_DIM),
        ]):
            ang = math.radians(self._angulo * r * -0.4 + i * 30)
            raio = 200 + i * 15
            x = CX + raio * math.cos(ang)
            y = CY + raio * math.sin(ang)
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill=c, outline="")

        # Labels de telemetria
        y_base = 380
        dados = [
            (f"ENERGIA  : {85 + int(15 * self._pulso):3d}%", 80),
            (f"LATÊNCIA : {12 + int(8 * self._pulso):3d}ms", 80),
            (f"CANAL    : pt-BR", 80),
        ]
        for texto, x in dados:
            self.canvas.create_text(
                x, y_base, text=texto, fill=CYAN_DIM,
                font=("Consolas", 7), anchor="w",
            )
            y_base += 14

        y_base = 380
        dados2 = [
            (f"MOTOR    : Google STT", WIN_W - 80),
            (f"MODO     : CONTÍNUO",   WIN_W - 80),
            (f"STATUS   : {self._status[:10]}", WIN_W - 80),
        ]
        for texto, x in dados2:
            self.canvas.create_text(
                x, y_base, text=texto, fill=CYAN_DIM,
                font=("Consolas", 7), anchor="e",
            )
            y_base += 14

    # ── Processar fila de eventos (thread-safe) ──────────────────────────────

    def _processar_fila(self):
        try:
            while True:
                tipo, valor = self._fila.get_nowait()
                if tipo == "status":
                    self._aplicar_status(valor)
                elif tipo == "log":
                    tag, linha = valor
                    self._adicionar_log(linha, tag)
                elif tipo == "mic_nome":
                    self.label_mic_nome.configure(text=valor)
                    self._microfone_atual = valor
        except queue.Empty:
            pass
        self.root.after(80, self._processar_fila)

    def _aplicar_status(self, texto: str):
        self._status = texto.upper()
        self.label_status.configure(text=texto.upper())

        cores_dot = {
            "OUVINDO":      GREEN,
            "PROCESSANDO":  ORANGE,
            "PAUSADO":      RED,
            "ERRO":         RED,
            "INICIALIZANDO": CYAN_DIM,
        }
        cor_dot = CYAN_DIM
        for k, v in cores_dot.items():
            if k in self._status:
                cor_dot = v
                break
        self.label_status_dot.configure(fg=cor_dot)
        self.label_status.configure(fg=self._cor_status())

    def _adicionar_log(self, texto: str, tag: str = "sistema"):
        ts = time.strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{ts}] ", "ts")
        self.log.insert("end", texto + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ── API pública (thread-safe) ────────────────────────────────────────────

    def atualizar_status(self, texto: str):
        self._fila.put(("status", texto))

    def registrar_log(self, texto: str, tag: str = "sistema"):
        """
        tag pode ser: "voz", "jarvis", "sistema", "erro", "texto"
        """
        self._fila.put(("log", (tag, texto)))

    def atualizar_microfone(self, nome: str):
        self._fila.put(("mic_nome", nome))

    # ── Entrada manual ───────────────────────────────────────────────────────

    def _limpar_placeholder(self, event=None):
        if self.entrada.get() == "Digite um comando ou fale...":
            self.entrada.delete(0, "end")
            self.entrada.configure(fg=WHITE)

    def _restaurar_placeholder(self, event=None):
        if not self.entrada.get():
            self.entrada.insert(0, "Digite um comando ou fale...")
            self.entrada.configure(fg=GRAY)

    def _enviar_manual(self, event=None):
        texto = self.entrada.get().strip()
        if not texto or texto == "Digite um comando ou fale...":
            return
        self.entrada.delete(0, "end")
        self.registrar_log(f"Você (texto): {texto}", "texto")
        self.on_comando_manual(texto)

    # ── Diálogo de seleção de microfone ─────────────────────────────────────

    def _abrir_dialogo_microfone(self):
        """Abre janela modal para listar e escolher o microfone."""
        mics = []
        if self.on_detectar_microfones:
            mics = self.on_detectar_microfones()

        dialog = tk.Toplevel(self.root)
        dialog.title("Selecionar Microfone")
        dialog.configure(bg=BG)
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog, text="SELECIONAR DISPOSITIVO DE ENTRADA",
            font=FONT_STATUS, fg=CYAN, bg=BG,
        ).pack(pady=(16, 6))

        tk.Label(
            dialog,
            text="Escolha o microfone correto e clique em Usar Este:",
            font=FONT_SMALL, fg=GRAY, bg=BG,
        ).pack(pady=(0, 10))

        frame_lista = tk.Frame(dialog, bg=BG2)
        frame_lista.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        lista = tk.Listbox(
            frame_lista, bg=PANEL_BG, fg=WHITE, font=FONT_LOG,
            selectbackground=CYAN_DIM, selectforeground=WHITE,
            bd=0, highlightthickness=0, activestyle="none",
        )
        scroll_l = tk.Scrollbar(frame_lista, command=lista.yview, bg=BG2,
                                 troughcolor=BG2, bd=0)
        lista.configure(yscrollcommand=scroll_l.set)
        scroll_l.pack(side="right", fill="y")
        lista.pack(fill="both", expand=True)

        lista.insert("end", "[Padrão do sistema]")
        for idx, nome in mics:
            lista.insert("end", f"[{idx}] {nome}")

        lista.select_set(0)

        def usar_selecionado():
            sel = lista.curselection()
            if not sel:
                return
            i = sel[0]
            if i == 0:
                device_index = None
                nome_display = "Padrão do sistema"
            else:
                device_index, nome_display = mics[i - 1]
            if self.on_salvar_microfone:
                self.on_salvar_microfone(device_index)
            self.atualizar_microfone(nome_display)
            self.registrar_log(f"[sistema] Microfone alterado para: {nome_display}", "sistema")
            dialog.destroy()

        tk.Button(
            dialog, text="✔  USAR ESTE",
            command=usar_selecionado,
            bg=CYAN, fg=BG, font=("Consolas", 10, "bold"),
            relief="flat", padx=16, pady=6, cursor="hand2",
        ).pack(pady=(0, 16))

    # ── Fechar ───────────────────────────────────────────────────────────────

    def _ao_fechar(self):
        self.on_fechar()
        self.root.destroy()

    def rodar(self):
        self.root.mainloop()
