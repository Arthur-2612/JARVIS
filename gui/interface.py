"""
Interface HUD Premium do JARVIS v4.5 - Ultra High-Definition & Smooth UI.

Design sci-fi modernizado de alta fidelidade com:
- Suporte a High-DPI Awareness (sem pixels borrados/esticados no Windows).
- Placa de título com alto contraste e proteção visual (100% legível).
- Modo SILENCIADO com dois botões distintos (Microfone Cortado 🎙️❌ e Normal 🎙️).
- Arc-Reactor HD com renderização vetorial suave, aura de brilho e geometria hexagonal.
- Efeitos visuais de hover interativos e alteração de foco.
- Suporte a TELA CHEIA (Fullscreen F11 ou botão ⛶ TELA CHEIA).
- Log de conversa estilizado com tags coloridas por falante.
- Painel de controle de microfone e entrada manual responsiva.
"""

import sys
import os
import queue
import math
import time
import ctypes
import tkinter as tk
from tkinter import font as tkfont


# ── Ativação de High-DPI no Windows (Elimina Pixelado/Desfoque) ─────────────
def _ativar_dpi_awareness():
    if sys.platform == "win32":
        try:
            # DPI Awareness Per-Monitor V2 (Windows 10 1703+)
            ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
        except Exception:
            try:
                # DPI Awareness Per-Monitor (Windows 8.1+)
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                try:
                    # DPI Awareness System (Windows Vista / 7)
                    ctypes.windll.user32.SetProcessDpiAware()
                except Exception:
                    pass


# ── Paleta de Cores Sci-Fi Modernizada ──────────────────────────────────────
BG           = "#040814"       # Deep Obsidian Space Dark
BG_CARD      = "#081024"       # Dark Glass Card Background
BG_PANEL     = "#060b18"       # Log & Input Panel Dark
BORDER_DIM   = "#102040"       # Subtle Frame Border
BORDER_GLOW  = "#00a2ff"       # Active Neon Glow Border

CYAN         = "#00f0ff"       # Neon Electric Cyan
CYAN_DIM     = "#005577"       # Muted Blue-Cyan
CYAN_GLOW    = "#80f8ff"       # Intense Bright Cyan Glow
BLUE_NEON    = "#0077ff"       # Electric Blue
GOLD         = "#ffd000"       # Jarvis Golden Accent
GREEN        = "#00ff9d"       # Status OK / User Text Green
RED          = "#ff2a5f"       # Error / Paused Red
ORANGE       = "#ff9d00"       # Processing Amber
WHITE        = "#f0f6fc"       # Primary Crisp White
GRAY         = "#6e82a0"       # Secondary Muted Slate

# ── Fontes ───────────────────────────────────────────────────────────────────
FONT_TITLE   = ("Segoe UI", 16, "bold")
FONT_SUBTITLE= ("Consolas", 8)
FONT_STATUS  = ("Segoe UI", 11, "bold")
FONT_LOG     = ("Consolas", 10)
FONT_INPUT   = ("Segoe UI", 10)
FONT_BTN     = ("Segoe UI", 9, "bold")
FONT_SMALL   = ("Consolas", 8, "bold")
FONT_MIC     = ("Segoe UI", 9)

# ── Tamanho inicial da janela ────────────────────────────────────────────────
WIN_W, WIN_H = 760, 880


class InterfaceJarvis:
    def __init__(self, on_comando_manual, on_fechar, on_detectar_microfones=None, on_salvar_microfone=None, on_alternar_mudo=None):
        self.on_comando_manual       = on_comando_manual
        self.on_fechar               = on_fechar
        self.on_detectar_microfones  = on_detectar_microfones
        self.on_salvar_microfone     = on_salvar_microfone
        self.on_alternar_mudo        = on_alternar_mudo

        self._fila   = queue.Queue()
        self._angulo = 0.0
        self._status = "INICIALIZANDO"
        self._pulso  = 0.0          # 0..1 para anel pulsante
        self._pulso_dir = 1
        self._grade_offset = 0.0
        self._eh_fullscreen = False
        self._mutado = False

        self._microfone_atual = "Detectando..."
        self._mics_disponiveis: list[tuple[int, str]] = []

        # Ativa renderização DPI nítida
        _ativar_dpi_awareness()

        self._construir_janela()
        self._construir_header()
        self._construir_canvas()
        self._construir_log()
        self._construir_mic_panel()
        self._construir_entrada()

        self._animar()
        self.root.after(50, self._processar_fila)

    # ── Construção da Janela Principal ───────────────────────────────────────

    def _construir_janela(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S — Sistema Operacional de IA")
        self.root.configure(bg=BG)
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.minsize(680, 780)
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        # Atalhos de Tela Cheia
        self.root.bind("<F11>", self.alternar_tela_cheia)
        self.root.bind("<Escape>", self.desativar_tela_cheia)

    # ── Header & Badge de Status ─────────────────────────────────────────────

    def _construir_header(self):
        self.frame_header = tk.Frame(self.root, bg=BG_CARD, bd=1, relief="flat", highlightbackground=BORDER_DIM, highlightthickness=1)
        self.frame_header.pack(fill="x", padx=16, pady=(14, 6))

        # Container interno do Header
        inner = tk.Frame(self.frame_header, bg=BG_CARD)
        inner.pack(fill="x", padx=12, pady=10)

        # Dot indicador pulsante
        self.label_status_dot = tk.Label(
            inner, text="●", font=("Segoe UI", 16),
            fg=GREEN, bg=BG_CARD,
        )
        self.label_status_dot.pack(side="left", padx=(4, 8))

        # Texto do Status
        self.label_status = tk.Label(
            inner, text="INICIALIZANDO...",
            font=FONT_STATUS, fg=CYAN, bg=BG_CARD,
        )
        self.label_status.pack(side="left")

        # Versão do Sistema à direita
        lbl_sys = tk.Label(
            inner, text="SYSTEM ONLINE v4.5  ◈  CORE ACTIVE",
            font=FONT_SUBTITLE, fg=GRAY, bg=BG_CARD,
        )
        lbl_sys.pack(side="right", padx=6)

    # ── Canvas do Arc-Reactor ────────────────────────────────────────────────

    def _construir_canvas(self):
        frame_canvas = tk.Frame(self.root, bg=BG)
        frame_canvas.pack(fill="both", expand=True, padx=16, pady=4)

        self.canvas = tk.Canvas(
            frame_canvas, width=WIN_W, height=380,
            bg=BG, highlightthickness=0, bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

    # ── Log de Conversa Estilizado ───────────────────────────────────────────

    def _construir_log(self):
        frame_log_outer = tk.Frame(
            self.root, bg=BG_CARD, bd=1,
            highlightbackground=BORDER_DIM, highlightthickness=1,
        )
        frame_log_outer.pack(fill="both", expand=True, padx=16, pady=6)

        # Cabeçalho do Log
        frame_head = tk.Frame(frame_log_outer, bg=BG_CARD)
        frame_head.pack(fill="x", padx=12, pady=(8, 4))

        tk.Label(
            frame_head, text="◈  REGISTRO DE COMUNICAÇÃO EM TEMPO REAL",
            font=FONT_SMALL, fg=CYAN_DIM, bg=BG_CARD, anchor="w",
        ).pack(side="left")

        # Área de Texto
        frame_text = tk.Frame(frame_log_outer, bg=BG_PANEL)
        frame_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log = tk.Text(
            frame_text, bg=BG_PANEL, fg=WHITE,
            insertbackground=CYAN, font=FONT_LOG,
            bd=0, wrap="word", state="disabled",
            selectbackground=BLUE_NEON, selectforeground=WHITE,
            height=8, padx=8, pady=8,
        )
        scroll = tk.Scrollbar(
            frame_text, command=self.log.yview, bg=BG_CARD,
            troughcolor=BG_PANEL, bd=0, relief="flat", width=10,
        )
        self.log.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)

        # Tags de Cores para mensagens
        self.log.tag_configure("voz",     foreground=CYAN_GLOW, font=("Consolas", 10, "bold"))
        self.log.tag_configure("jarvis",  foreground=GOLD,      font=("Consolas", 10, "bold"))
        self.log.tag_configure("sistema", foreground=GRAY)
        self.log.tag_configure("erro",    foreground=RED,       font=("Consolas", 10, "bold"))
        self.log.tag_configure("texto",   foreground=GREEN,     font=("Consolas", 10, "bold"))
        self.log.tag_configure("ts",      foreground=CYAN_DIM)

    # ── Painel do Microfone & Controles de Mudo ──────────────────────────────────

    def _construir_mic_panel(self):
        self.frame_mic = tk.Frame(
            self.root, bg=BG_CARD, bd=1,
            highlightbackground=BORDER_DIM, highlightthickness=1,
        )
        self.frame_mic.pack(fill="x", padx=16, pady=4)

        # ── Linha 1: Dispositivo Atual e utilitários ──
        row1 = tk.Frame(self.frame_mic, bg=BG_CARD)
        row1.pack(fill="x", padx=10, pady=(6, 2))

        tk.Label(
            row1, text="🎙 DISPOSITIVO:",
            font=FONT_SMALL, fg=CYAN_DIM, bg=BG_CARD,
        ).pack(side="left", padx=(4, 4))

        self.label_mic_nome = tk.Label(
            row1, text="Detectando...",
            font=FONT_MIC, fg=WHITE, bg=BG_CARD, anchor="w",
        )
        self.label_mic_nome.pack(side="left", padx=2)

        # Botão de Tela Cheia
        btn_fullscreen = tk.Button(
            row1, text="⛶ TELA CHEIA",
            command=self.alternar_tela_cheia,
            bg=BORDER_DIM, fg=CYAN, font=FONT_BTN,
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
            activebackground=BLUE_NEON, activeforeground=WHITE,
        )
        btn_fullscreen.pack(side="right", padx=(2, 0))

        # Botão de Trocar Microfone
        btn_detectar = tk.Button(
            row1, text="⟳ DETECTAR MIC",
            command=self._abrir_dialogo_microfone,
            bg=BORDER_DIM, fg=CYAN, font=FONT_BTN,
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
            activebackground=BLUE_NEON, activeforeground=WHITE,
        )
        btn_detectar.pack(side="right", padx=2)

        # ── Linha 2: Barra Destaque de MUTE / UNMUTE ──
        row2 = tk.Frame(self.frame_mic, bg=BG_PANEL, bd=1, highlightbackground=BORDER_DIM, highlightthickness=1)
        row2.pack(fill="x", padx=10, pady=(4, 8))

        inner_row2 = tk.Frame(row2, bg=BG_PANEL)
        inner_row2.pack(fill="x", padx=8, pady=4)

        tk.Label(
            inner_row2, text="MODO DE ESCUTA:",
            font=FONT_SMALL, fg=CYAN_GLOW, bg=BG_PANEL,
        ).pack(side="left", padx=(4, 10))

        # Botão SILENCIAR (Microfone Cortado 🎙️❌)
        self.btn_mutar = tk.Button(
            inner_row2, text="🎙️❌ SILENCIAR (MUTE)",
            command=lambda: self.definir_mudo(True),
            bg=BORDER_DIM, fg=GRAY, font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, padx=14, pady=5, cursor="hand2",
            activebackground=RED, activeforeground=WHITE,
        )
        self.btn_mutar.pack(side="left", padx=4)

        # Botão DESMUTAR (Microfone Normal 🎙️)
        self.btn_desmutar = tk.Button(
            inner_row2, text="🎙️ DESMUTAR (OUVINDO)",
            command=lambda: self.definir_mudo(False),
            bg="#006644", fg=WHITE, font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, padx=14, pady=5, cursor="hand2",
            activebackground=GREEN, activeforeground=BG,
        )
        self.btn_desmutar.pack(side="left", padx=4)

        # Efeitos de Hover nos botões
        for b in (btn_fullscreen, btn_detectar):
            b.bind("<Enter>", lambda e, btn=b: btn.configure(bg="#18325a"))
            b.bind("<Leave>", lambda e, btn=b: btn.configure(bg=BORDER_DIM))


    # ── Controle do Modo Muto (Silenciado) ───────────────────────────────────

    def definir_mudo(self, mutado: bool):
        self._mutado = mutado
        if mutado:
            self.btn_mutar.configure(bg=RED, fg=WHITE)
            self.btn_desmutar.configure(bg=BORDER_DIM, fg=GRAY)
            self.atualizar_status("SILENCIADO")
            self.registrar_log("[sistema] Modo SILENCIADO ativado (Microfone desativado).", "erro")
        else:
            self.btn_mutar.configure(bg=BORDER_DIM, fg=GRAY)
            self.btn_desmutar.configure(bg="#005533", fg=WHITE)
            self.atualizar_status("OUVINDO...")
            self.registrar_log("[sistema] Microfone REATIVADO (Ouvindo).", "sistema")

        if self.on_alternar_mudo:
            self.on_alternar_mudo(self._mutado)

    # ── Campo de Entrada de Texto ────────────────────────────────────────────

    def _construir_entrada(self):
        self.frame_entrada_outer = tk.Frame(
            self.root, bg=BG_CARD, bd=1,
            highlightbackground=BORDER_DIM, highlightthickness=1,
        )
        self.frame_entrada_outer.pack(fill="x", padx=16, pady=(4, 16))

        inner = tk.Frame(self.frame_entrada_outer, bg=BG_CARD)
        inner.pack(fill="x", padx=8, pady=6)

        tk.Label(
            inner, text="▶",
            font=("Segoe UI", 11, "bold"), fg=CYAN, bg=BG_CARD,
        ).pack(side="left", padx=(8, 4))

        # Frame interno para simular borda de foco na entrada
        self.frame_input_border = tk.Frame(inner, bg=BORDER_DIM, bd=1)
        self.frame_input_border.pack(side="left", fill="x", expand=True, padx=4)

        self.entrada = tk.Entry(
            self.frame_input_border, bg=BG_PANEL, fg=WHITE,
            insertbackground=CYAN, font=FONT_INPUT,
            relief="flat", bd=0,
        )
        self.entrada.pack(fill="x", expand=True, ipady=6, padx=8)
        self.entrada.bind("<Return>", self._enviar_manual)
        self.entrada.insert(0, "Digite um comando ou fale com o JARVIS...")
        self.entrada.configure(fg=GRAY)
        self.entrada.bind("<FocusIn>",  self._ao_focar_entrada)
        self.entrada.bind("<FocusOut>", self._ao_desfocar_entrada)

        self.btn_enviar = tk.Button(
            inner, text="ENVIAR",
            command=self._enviar_manual,
            bg=BLUE_NEON, fg=WHITE, font=FONT_BTN,
            relief="flat", bd=0, padx=16, pady=6, cursor="hand2",
            activebackground=CYAN, activeforeground=BG,
        )
        self.btn_enviar.pack(side="right", padx=(6, 4))
        self.btn_enviar.bind("<Enter>", lambda e: self.btn_enviar.configure(bg=CYAN, fg=BG))
        self.btn_enviar.bind("<Leave>", lambda e: self.btn_enviar.configure(bg=BLUE_NEON, fg=WHITE))

    def _ao_focar_entrada(self, event=None):
        self.frame_input_border.configure(bg=CYAN)
        if self.entrada.get() == "Digite um comando ou fale com o JARVIS...":
            self.entrada.delete(0, "end")
            self.entrada.configure(fg=WHITE)

    def _ao_desfocar_entrada(self, event=None):
        self.frame_input_border.configure(bg=BORDER_DIM)
        if not self.entrada.get().strip():
            self.entrada.insert(0, "Digite um comando ou fale com o JARVIS...")
            self.entrada.configure(fg=GRAY)

    # ── Animação do HUD ──────────────────────────────────────────────────────

    def _animar(self):
        self._angulo = (self._angulo + 1.5) % 360
        self._pulso  += 0.03 * self._pulso_dir
        if self._pulso >= 1.0:
            self._pulso = 1.0
            self._pulso_dir = -1
        elif self._pulso <= 0.0:
            self._pulso = 0.0
            self._pulso_dir = 1
        self._grade_offset = (self._grade_offset + 0.5) % 40

        self._desenhar_cena()
        self.root.after(30, self._animar)

    def _cor_status(self):
        s = self._status
        if "SILENCIADO" in s or "MUTADO" in s:
            return RED
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
        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 300)
        cx = w // 2
        cy = h // 2

        self._desenhar_grade(w, h)
        self._desenhar_aura_glow(cx, cy)
        self._desenhar_arc_reactor(cx, cy)
        self._desenhar_titulo(cx, cy)
        self._desenhar_telemetria_hud(cx, cy, w, h)

    # Grade Holográfica com linhas finas e pontos de interseção
    def _desenhar_grade(self, w, h):
        off = self._grade_offset
        cor_linha = "#081326"
        step = 40
        for x in range(-step, w + step, step):
            px = x + off
            self.canvas.create_line(px, 0, px, h, fill=cor_linha, width=1)
        for y in range(-step, h + step, step):
            py = y + off
            self.canvas.create_line(0, py, w, py, fill=cor_linha, width=1)

    # Simulador de Brilho Suave (Aura Radial)
    def _desenhar_aura_glow(self, cx, cy):
        status_cor = self._cor_status()
        is_active = "OUVINDO" in self._status or "PROCESSANDO" in self._status
        
        # Camadas concêntricas para simular gradiente de luz suave
        glow_colors = [
            ("#040f24", 210),
            ("#071a38", 180),
            ("#0a254c", 150),
            ("#0c3266", 120),
        ] if not is_active else [
            ("#051c2e", 230 + int(20 * self._pulso)),
            ("#0a334f", 190 + int(15 * self._pulso)),
            ("#0e4b73", 150 + int(10 * self._pulso)),
            ("#12669c", 110 + int(5 * self._pulso)),
        ]

        for color, radius in glow_colors:
            self.canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                fill=color, outline="", width=0,
            )

    # Arc-Reactor HD com Geometria Suave
    def _desenhar_arc_reactor(self, cx, cy):
        status_cor = self._cor_status()

        # Pulso Externo quando ouvindo/processando
        if "OUVINDO" in self._status:
            r_pulso = 175 + int(18 * math.sin(self._pulso * math.pi))
            self.canvas.create_oval(
                cx - r_pulso, cy - r_pulso,
                cx + r_pulso, cy + r_pulso,
                outline=BLUE_NEON, width=2,
            )
            self.canvas.create_oval(
                cx - r_pulso + 8, cy - r_pulso + 8,
                cx + r_pulso - 8, cy + r_pulso - 8,
                outline=CYAN_GLOW, width=1,
            )

        # Anéis Giratórios Interiores
        aneis = [
            (160, 2, CYAN_DIM,    0.40, 290),
            (140, 3, status_cor, -0.70, 310),
            (118, 2, BLUE_NEON,   1.10, 270),
            (96,  3, status_cor, -1.40, 320),
            (76,  2, CYAN_GLOW,   1.80, 280),
        ]
        for raio, larg, cor, vel, extent in aneis:
            inicio = (self._angulo * vel) % 360
            self.canvas.create_arc(
                cx - raio, cy - raio, cx + raio, cy + raio,
                start=inicio, extent=extent,
                style="arc", outline=cor, width=larg,
            )

        # Núcleo Hexagonal Suave (calculado trigonometricamente)
        hex_points = []
        r_hex = 52
        ang_off = math.radians(self._angulo * 0.3)
        for i in range(6):
            a = ang_off + i * (math.pi / 3)
            hx = cx + r_hex * math.cos(a)
            hy = cy + r_hex * math.sin(a)
            hex_points.extend([hx, hy])

        self.canvas.create_polygon(
            hex_points, fill="#071b28", outline=status_cor, width=2,
        )

        # Círculo Núcleo Interior
        for r, cor in [(36, "#0a293c"), (26, "#0d3c59"), (16, CYAN_GLOW)]:
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=cor, outline="", width=0,
            )

        # Brilho Central do Core
        r_core = 10 + int(3 * math.sin(self._pulso * math.pi))
        self.canvas.create_oval(
            cx - r_core, cy - r_core, cx + r_core, cy + r_core,
            fill=WHITE, outline=CYAN_GLOW, width=2,
        )

        # Partículas Orbitais Suaves
        for i in range(4):
            a_orb = math.radians(self._angulo * 0.8 + i * 90)
            r_orb = 128
            ox = cx + r_orb * math.cos(a_orb)
            oy = cy + r_orb * math.sin(a_orb)
            self.canvas.create_oval(ox-4, oy-4, ox+4, oy+4, fill=CYAN_GLOW, outline=BLUE_NEON)

    # Título do HUD com Placa Escura de Alto Contraste (Legibilidade Máxima)
    def _desenhar_titulo(self, cx, cy):
        # Placa dark glass no topo do canvas para legibilidade e contraste perfeitos
        pw, ph = 320, 48
        px1, py1 = cx - pw // 2, 12
        px2, py2 = cx + pw // 2, 12 + ph

        # Fundo escuro Obsidian com borda Neon Blue
        self.canvas.create_rectangle(
            px1, py1, px2, py2,
            fill="#030818", outline=BLUE_NEON, width=1.5,
        )
        # Cantos decorativos da placa de título
        self.canvas.create_line(px1, py1, px1 + 12, py1, fill=CYAN_GLOW, width=2)
        self.canvas.create_line(px1, py1, px1, py1 + 12, fill=CYAN_GLOW, width=2)
        self.canvas.create_line(px2 - 12, py2, px2, py2, fill=CYAN_GLOW, width=2)
        self.canvas.create_line(px2, py2 - 12, px2, py2, fill=CYAN_GLOW, width=2)

        # Sombras e Texto com alto contraste (Preto + Ciano Nítido)
        self.canvas.create_text(
            cx + 1, 29, text="J.A.R.V.I.S",
            fill="#000000", font=("Segoe UI", 16, "bold"),
        )
        self.canvas.create_text(
            cx, 28, text="J.A.R.V.I.S",
            fill=CYAN_GLOW, font=("Segoe UI", 16, "bold"),
        )
        self.canvas.create_line(
            cx - 60, 41, cx + 60, 41,
            fill=CYAN_DIM, width=1,
        )
        self.canvas.create_text(
            cx, 49, text="INTELLIGENT SYSTEM ARCHITECTURE v4.5",
            fill=WHITE, font=("Consolas", 7, "bold"),
        )

    # Molduras e Telemetria Sci-Fi
    def _desenhar_telemetria_hud(self, cx, cy, w, h):
        # Cantos Decorativos HD
        pad = 12
        length = 24
        cantos = [
            (pad, pad, pad + length, pad), (pad, pad, pad, pad + length),
            (w - pad - length, pad, w - pad, pad), (w - pad, pad, w - pad, pad + length),
            (pad, h - pad, pad + length, h - pad), (pad, h - pad - length, pad, h - pad),
            (w - pad - length, h - pad, w - pad, h - pad), (w - pad, h - pad - length, w - pad, h - pad),
        ]
        for x1, y1, x2, y2 in cantos:
            self.canvas.create_line(x1, y1, x2, y2, fill=CYAN_DIM, width=2)

        # Painéis de Telemetria Inferiores
        y_base = max(h - 50, 160)
        t_left = [
            f"PWR CORE : {92 + int(8 * math.sin(self._pulso * math.pi)):3d}%",
            f"LATENCY  : {10 + int(5 * math.sin(self._pulso * math.pi)):3d} ms",
            f"VOICE IN : {'MUTED' if self._mutado else 'ACTIVE'}",
        ]
        for idx, texto in enumerate(t_left):
            self.canvas.create_text(
                24, y_base + idx * 14, text=texto,
                fill=CYAN_DIM, font=("Consolas", 8), anchor="w",
            )

        t_right = [
            f"STT ENG  : Google Speech",
            f"AUDIO CH : STEREO 48K",
            f"STATE    : {self._status[:12]}",
        ]
        for idx, texto in enumerate(t_right):
            self.canvas.create_text(
                w - 24, y_base + idx * 14, text=texto,
                fill=CYAN_DIM, font=("Consolas", 8), anchor="e",
            )

    # ── Processamento de Fila Thread-Safe ────────────────────────────────────

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
        self.root.after(50, self._processar_fila)

    def _aplicar_status(self, texto: str):
        self._status = texto.upper()
        self.label_status.configure(text=self._status)

        cores_dot = {
            "SILENCIADO":   RED,
            "MUTADO":       RED,
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

    # ── API Pública (Thread-Safe) ────────────────────────────────────────────

    def atualizar_status(self, texto: str):
        self._fila.put(("status", texto))

    def registrar_log(self, texto: str, tag: str = "sistema"):
        self._fila.put(("log", (tag, texto)))

    def atualizar_microfone(self, nome: str):
        self._fila.put(("mic_nome", nome))

    # ── Controle de Tela Cheia ───────────────────────────────────────────────

    def alternar_tela_cheia(self, event=None):
        self._eh_fullscreen = not getattr(self, "_eh_fullscreen", False)
        self.root.attributes("-fullscreen", self._eh_fullscreen)
        if not self._eh_fullscreen:
            self.root.geometry(f"{WIN_W}x{WIN_H}")

    def desativar_tela_cheia(self, event=None):
        if getattr(self, "_eh_fullscreen", False):
            self._eh_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.root.geometry(f"{WIN_W}x{WIN_H}")

    # ── Envio de Comando Manual ──────────────────────────────────────────────

    def _enviar_manual(self, event=None):
        texto = self.entrada.get().strip()
        if not texto or texto == "Digite um comando ou fale com o JARVIS...":
            return
        self.entrada.delete(0, "end")
        self.registrar_log(f"Você (texto): {texto}", "texto")
        self.on_comando_manual(texto)

    # ── Diálogo Modal de Seleção de Microfone ────────────────────────────────

    def _abrir_dialogo_microfone(self):
        mics = []
        if self.on_detectar_microfones:
            mics = self.on_detectar_microfones()

        dialog = tk.Toplevel(self.root)
        dialog.title("Selecionar Dispositivo de Entrada")
        dialog.configure(bg=BG)
        dialog.geometry("520x420")
        dialog.transient(self.root)
        dialog.grab_set()

        frame_modal = tk.Frame(
            dialog, bg=BG_CARD, bd=1,
            highlightbackground=BORDER_DIM, highlightthickness=1,
        )
        frame_modal.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            frame_modal, text="SELECIONAR MICROFONE",
            font=FONT_STATUS, fg=CYAN, bg=BG_CARD,
        ).pack(pady=(16, 4))

        tk.Label(
            frame_modal,
            text="Escolha o dispositivo de entrada ativo e clique em Confirmar:",
            font=FONT_SMALL, fg=GRAY, bg=BG_CARD,
        ).pack(pady=(0, 10))

        frame_lista = tk.Frame(frame_modal, bg=BG_PANEL)
        frame_lista.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        lista = tk.Listbox(
            frame_lista, bg=BG_PANEL, fg=WHITE, font=FONT_LOG,
            selectbackground=BLUE_NEON, selectforeground=WHITE,
            bd=0, highlightthickness=0, activestyle="none",
        )
        scroll_l = tk.Scrollbar(
            frame_lista, command=lista.yview, bg=BG_CARD,
            troughcolor=BG_PANEL, bd=0, relief="flat", width=10,
        )
        lista.configure(yscrollcommand=scroll_l.set)

        scroll_l.pack(side="right", fill="y")
        lista.pack(fill="both", expand=True, padx=6, pady=6)

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

        btn_confirmar = tk.Button(
            frame_modal, text="✔  USAR ESTE DISPOSITIVO",
            command=usar_selecionado,
            bg=BLUE_NEON, fg=WHITE, font=FONT_BTN,
            relief="flat", bd=0, padx=18, pady=8, cursor="hand2",
            activebackground=CYAN, activeforeground=BG,
        )
        btn_confirmar.pack(pady=(0, 16))
        btn_confirmar.bind("<Enter>", lambda e: btn_confirmar.configure(bg=CYAN, fg=BG))
        btn_confirmar.bind("<Leave>", lambda e: btn_confirmar.configure(bg=BLUE_NEON, fg=WHITE))

    # ── Finalização & Eventos ────────────────────────────────────────────────

    def _ao_fechar(self):
        self.on_fechar()
        self.root.destroy()

    def rodar(self):
        self.root.mainloop()
