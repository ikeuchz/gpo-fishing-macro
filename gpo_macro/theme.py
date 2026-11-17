from tkinter import ttk

BG = '#0b1220'
CARD = '#141f32'
TEXT = '#e5edf9'
MUTED = '#9eafc7'
ACCENT = '#45dbc2'


def apply(root):
    root.configure(bg=BG)
    root.option_add('*Font', ('Segoe UI', 10))
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=BG, foreground=TEXT, font=('Segoe UI', 10))
    style.configure('TFrame', background=BG)
    style.configure('TLabel', background=BG, foreground=TEXT)
    style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'))
    style.configure('Muted.TLabel', foreground=MUTED)
    style.configure('Status.TLabel', background=CARD, foreground=ACCENT, padding=14)
    style.configure('TButton', background='#22314a', foreground=TEXT, padding=(14, 9), borderwidth=0)
    style.map('TButton', background=[('active', '#304766'), ('disabled', '#182337')])
    style.configure('Accent.TButton', background=ACCENT, foreground=BG, font=('Segoe UI', 10, 'bold'))
    style.map('Accent.TButton', background=[('active', '#83eddb'), ('disabled', '#224c4a')])
    style.configure('TEntry', fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT, padding=6)
    style.configure('TCheckbutton', background=BG, foreground=TEXT, padding=4)
    style.map('TCheckbutton', background=[('active', CARD)])
    style.configure('TNotebook', background=BG, borderwidth=0)
    style.configure('TNotebook.Tab', background=CARD, foreground=MUTED, padding=(17, 10))
    style.map('TNotebook.Tab', background=[('selected', '#22314a')], foreground=[('selected', ACCENT)])
    style.configure('Vertical.TScrollbar', background='#304766', troughcolor=BG)
    style.configure('Card.TFrame', background=CARD)
    style.configure('Card.TLabel', background=CARD, foreground=TEXT)
    style.configure('CardTitle.TLabel', background=CARD, foreground=TEXT, font=('Segoe UI', 13, 'bold'))
    style.configure('CardHint.TLabel', background=CARD, foreground=MUTED, font=('Segoe UI', 9))
    style.configure('Card.TCheckbutton', background=CARD, foreground=TEXT, padding=4)
    style.map('Card.TCheckbutton', background=[('active', CARD)])
    style.configure('TCombobox', fieldbackground='#0e1728', foreground=TEXT, padding=6)
    style.map('TCombobox', fieldbackground=[('readonly', '#0e1728')], foreground=[('readonly', TEXT)])
