"""Tema visual centralizado do app (paleta, tipografia, estilos ttk).

Identidade "clube de tênis": sidebar slate profundo, acento terracota (saibro)
e conteúdo claro. Use as constantes daqui em vez de cores/fontes soltas para
manter tudo consistente.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

# Paleta ---------------------------------------------------------------------
BG          = "#eef1f5"   # fundo da área de conteúdo
SURFACE     = "#ffffff"   # cartões, tabelas, campos
SIDEBAR     = "#1e293b"   # menu lateral (slate)
SIDEBAR_HOV = "#33425a"   # hover de item do menu
SIDEBAR_TXT = "#cbd5e1"   # texto do menu
ACCENT      = "#c2410c"   # acento (terracota / saibro)
ACCENT_HOV  = "#ea580c"   # acento em hover
ACCENT_SOFT = "#fbe3d6"   # seleção de linha / realce suave
TEXT        = "#0f172a"   # texto principal
TEXT_MUTED  = "#64748b"   # texto secundário
BORDER      = "#dfe4ea"   # bordas / divisórias
ROW_ALT     = "#f5f7fa"   # linha alternada de tabela

# Tipografia -----------------------------------------------------------------
# Segoe UI é a fonte nativa do Windows (plataforma alvo do app); em outros
# sistemas o tkinter faz fallback para uma sans padrão.
FAMILY = "Segoe UI"

FONT_TITLE    = (FAMILY, 26, "bold")
FONT_SUBTITLE = (FAMILY, 16, "bold")
FONT_HEADING  = (FAMILY, 13, "bold")
FONT_BODY     = (FAMILY, 11)
FONT_SMALL    = (FAMILY, 10)
FONT_BUTTON   = (FAMILY, 11, "bold")


def setup(root: tk.Tk) -> None:
    """Aplica fontes padrão e estilos ttk. Chamar uma vez no app principal."""
    for named in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
        try:
            tkfont.nametofont(named).configure(family=FAMILY, size=11)
        except tk.TclError:
            pass

    root.configure(bg=BG)

    # Defaults para widgets tk clássicos (aplicam-se onde não houver override).
    root.option_add("*Button.background", ACCENT)
    root.option_add("*Button.foreground", "white")
    root.option_add("*Button.activeBackground", ACCENT_HOV)
    root.option_add("*Button.activeForeground", "white")
    root.option_add("*Button.relief", "flat")
    root.option_add("*Button.borderWidth", 0)
    root.option_add("*Button.padX", 14)
    root.option_add("*Button.padY", 8)
    root.option_add("*Button.cursor", "hand2")
    root.option_add("*Entry.relief", "flat")
    root.option_add("*Entry.background", SURFACE)
    root.option_add("*Entry.highlightThickness", 1)
    root.option_add("*Entry.highlightColor", ACCENT)
    root.option_add("*Entry.highlightBackground", BORDER)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Tabelas
    style.configure(
        "Treeview",
        background=SURFACE, fieldbackground=SURFACE, foreground=TEXT,
        rowheight=32, font=FONT_BODY, borderwidth=0,
    )
    style.map("Treeview",
              background=[("selected", ACCENT_SOFT)],
              foreground=[("selected", TEXT)])
    style.configure(
        "Treeview.Heading",
        background=SIDEBAR, foreground="white", font=FONT_HEADING,
        relief="flat", padding=(12, 9),
    )
    style.map("Treeview.Heading", background=[("active", SIDEBAR_HOV)])

    # Combobox
    style.configure(
        "TCombobox",
        padding=7, font=FONT_BODY,
        fieldbackground=SURFACE, background=SURFACE,
        bordercolor=BORDER, arrowcolor=SIDEBAR,
    )

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=BORDER, troughcolor=BG, borderwidth=0, arrowcolor=TEXT_MUTED)


def maximize(root: tk.Tk) -> None:
    """Maximiza a janela de forma compatível entre Windows e Linux/WSLg."""
    try:
        root.state("zoomed")            # Windows
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)   # maioria dos WMs Linux
        except tk.TclError:
            root.geometry("1280x800")


def make_button(parent, text, command, variant="primary", **kw):
    """Botão estilizado com hover. variant: primary | ghost | sidebar."""
    palette = {
        "primary": (ACCENT, "white", ACCENT_HOV, "white"),
        "ghost":   (SURFACE, TEXT, BG, TEXT),
        "sidebar": (SIDEBAR, SIDEBAR_TXT, SIDEBAR_HOV, "white"),
    }
    bg, fg, hover, hover_fg = palette[variant]
    btn = tk.Button(
        parent, text=text, command=command, font=FONT_BUTTON,
        bg=bg, fg=fg, activebackground=hover, activeforeground=hover_fg,
        relief="flat", bd=0, padx=16, pady=9, cursor="hand2",
        highlightthickness=0, anchor="w" if variant == "sidebar" else "center",
        **kw,
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover, fg=hover_fg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg, fg=fg))
    return btn
