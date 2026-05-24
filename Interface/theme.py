"""Tema visual centralizado do app — estilo Spotify (dark).

Paleta near-black com sidebar preta, cartões cinza-escuros, acento verde e
texto branco/cinza. Use as constantes daqui em vez de cores/fontes soltas.
O theming é aplicado globalmente (inclusive nos diálogos) via option_add +
estilos ttk, então telas que não setam cor explicitamente já saem escuras.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

# Paleta (Spotify) -----------------------------------------------------------
BG          = "#121212"   # base da área de conteúdo
SIDEBAR     = "#000000"   # menu lateral (preto)
SURFACE     = "#181818"   # cartões / tabelas
ELEV        = "#282828"   # superfície elevada / campos / hover
SIDEBAR_HOV = "#1a1a1a"
SIDEBAR_TXT = "#b3b3b3"   # texto do menu (cinza -> branco no hover)
ACCENT      = "#1ed760"   # verde Spotify
ACCENT_HOV  = "#1fdf64"
ACCENT_SOFT = "#233a2a"   # verde escuro p/ realces
TEXT        = "#ffffff"
TEXT_MUTED  = "#b3b3b3"
BORDER      = "#2a2a2a"
ROW_ALT     = "#1a1a1a"   # linha alternada de tabela

# Tipografia -----------------------------------------------------------------
# O tkinter não carrega fontes web (como a Circular da Spotify). Usa-se Segoe UI
# (nativa do Windows, alvo do app) com pesos/tamanhos para criar a hierarquia.
FAMILY = "Segoe UI"

FONT_TITLE    = (FAMILY, 26, "bold")
FONT_SUBTITLE = (FAMILY, 16, "bold")
FONT_HEADING  = (FAMILY, 12, "bold")
FONT_BODY     = (FAMILY, 11)
FONT_SMALL    = (FAMILY, 10)
FONT_BUTTON   = (FAMILY, 11, "bold")


def setup(root: tk.Tk) -> None:
    """Aplica fontes padrão e estilos (tk + ttk). Chamar uma vez no app."""
    for named in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
        try:
            tkfont.nametofont(named).configure(family=FAMILY, size=11)
        except tk.TclError:
            pass

    root.configure(bg=BG)

    # Defaults globais p/ widgets tk clássicos (escurece inclusive diálogos).
    opt = root.option_add
    opt("*background", BG)
    opt("*foreground", TEXT)
    opt("*Toplevel.background", BG)
    opt("*Frame.background", BG)
    opt("*Label.background", BG)
    opt("*Label.foreground", TEXT)
    # Botões: CTA verde com texto preto (assinatura Spotify).
    opt("*Button.background", ACCENT)
    opt("*Button.foreground", "#000000")
    opt("*Button.activeBackground", ACCENT_HOV)
    opt("*Button.activeForeground", "#000000")
    opt("*Button.relief", "flat")
    opt("*Button.borderWidth", "0")
    opt("*Button.padX", "16")
    opt("*Button.padY", "9")
    opt("*Button.cursor", "hand2")
    # Campos de texto.
    opt("*Entry.background", ELEV)
    opt("*Entry.foreground", TEXT)
    opt("*Entry.insertBackground", TEXT)
    opt("*Entry.relief", "flat")
    opt("*Entry.highlightThickness", "1")
    opt("*Entry.highlightColor", ACCENT)
    opt("*Entry.highlightBackground", BORDER)
    # Checkbutton.
    opt("*Checkbutton.background", BG)
    opt("*Checkbutton.foreground", TEXT)
    opt("*Checkbutton.activeBackground", BG)
    opt("*Checkbutton.activeForeground", TEXT)
    opt("*Checkbutton.selectColor", ELEV)
    # Lista do dropdown do Combobox.
    opt("*TCombobox*Listbox.background", ELEV)
    opt("*TCombobox*Listbox.foreground", TEXT)
    opt("*TCombobox*Listbox.selectBackground", ACCENT)
    opt("*TCombobox*Listbox.selectForeground", "#000000")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Tabelas
    style.configure(
        "Treeview",
        background=SURFACE, fieldbackground=SURFACE, foreground=TEXT,
        rowheight=34, font=FONT_BODY, borderwidth=0,
    )
    style.map("Treeview",
              background=[("selected", ELEV)],
              foreground=[("selected", "#ffffff")])
    style.configure(
        "Treeview.Heading",
        background="#000000", foreground=TEXT_MUTED, font=FONT_HEADING,
        relief="flat", padding=(12, 10),
    )
    style.map("Treeview.Heading",
              background=[("active", SURFACE)],
              foreground=[("active", TEXT)])

    # Combobox
    style.configure(
        "TCombobox",
        padding=7, foreground=TEXT, arrowcolor=TEXT,
        fieldbackground=ELEV, background=ELEV,
        bordercolor=BORDER, lightcolor=ELEV, darkcolor=ELEV,
    )
    style.map("TCombobox",
              fieldbackground=[("readonly", ELEV)],
              background=[("readonly", ELEV)],
              foreground=[("readonly", TEXT)])

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=ELEV, troughcolor=BG, borderwidth=0, arrowcolor=TEXT_MUTED)
    style.map("Vertical.TScrollbar", background=[("active", "#3a3a3a")])


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
        "primary": (ACCENT, "#000000", ACCENT_HOV, "#000000"),
        "ghost":   (ELEV, TEXT, "#3a3a3a", TEXT),
        "sidebar": (SIDEBAR, SIDEBAR_TXT, SIDEBAR, "#ffffff"),
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
