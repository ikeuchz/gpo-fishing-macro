"""Presentation adapter. Fishing methods are inherited from the original core."""
from pathlib import Path
import queue
import sys
import tkinter as tk
from tkinter import messagebox
from .original import OriginalMacro, core
from .hotkeys import parse_shortcut
from . import theme


class App(OriginalMacro):
    def __init__(self, root):
        self.ui_events = queue.SimpleQueue()
        self.pending_start = None
        self.compact_mode = False
        self.closing = False
        super().__init__(root)
        root.title('GPO Fishing — ikeuchz')
        root.geometry('720x780')
        root.resizable(True, True)
        root.minsize(640, 260)
        root.attributes('-topmost', True)
        assets = Path(__file__).parent/'assets'
        self.icon = tk.PhotoImage(file=str(assets/'app.png'))
        root.iconphoto(True, self.icon)
        if sys.platform == 'win32':
            root.iconbitmap(str(assets/'app.ico'))
        root.protocol('WM_DELETE_WINDOW', self.exit_app)
        root.after(50, self.pump)

    def load_settings(self):
        bindings = super().load_settings()
        if not self.settings_file.exists():
            bindings = {'start_stop': 'INSERT', 'change_area': 'HOME', 'exit': 'END'}
        return bindings

    def create_widgets(self):
        theme.apply(self.root)
        self.header = tk.Frame(self.root, bg=theme.BG)
        self.header.pack(fill='x', padx=18, pady=(14, 8))
        tk.Label(self.header, text='GPO Fishing', bg=theme.BG, fg=theme.TEXT,
                 font=('Segoe UI', 22, 'bold')).pack(anchor='w')
        tk.Label(self.header, text='IKEUCHZ  /  MOTOR ORIGINAL', bg=theme.BG,
                 fg=theme.ACCENT, font=('Segoe UI', 9)).pack(anchor='w')
        self.toolbar = tk.Frame(self.root, bg=theme.BG)
        self.toolbar.pack(fill='x', padx=18, pady=8)
        buttons = [('Iniciar em 3 segundos', self.start_delayed),
                   ('Parar / cancelar', self.stop_button),
                   ('Área / salvar área', self.area_button),
                   ('Atalhos', self.shortcuts_dialog),
                   ('Compactar / expandir', self.toggle_compact)]
        for column, (text, command) in enumerate(buttons):
            tk.Button(self.toolbar, text=text, command=command, relief='flat',
                      bg=theme.ACCENT if column == 0 else '#22314a',
                      fg=theme.BG if column == 0 else theme.TEXT,
                      padx=10, pady=8).grid(row=column//3, column=column%3, sticky='ew', padx=3, pady=3)
        for col in range(3):
            self.toolbar.columnconfigure(col, weight=1)
        self.summary = tk.Label(self.root, text='', anchor='w', justify='left',
                                bg=theme.CARD, fg=theme.ACCENT, padx=14, pady=10,
                                wraplength=650)
        self.summary.pack(fill='x', padx=18, pady=(0, 8))
        # These are the original controls with their original callbacks and fields.
        # In particular, all options for points, bait, fruit and PD gains remain.
        super().create_widgets()
        self.canvas.bind('<Configure>', self.fit_original_controls)
        self.skin(self.scrollable_frame)
        self.canvas.configure(bg=theme.BG, highlightthickness=0)
        self.scrollbar.configure(bg='#22314a', troughcolor=theme.BG)
        self.compact_mode = False

    def fit_original_controls(self, event):
        for item in self.canvas.find_all():
            if self.canvas.type(item) == 'window':
                self.canvas.itemconfigure(item, width=event.width)

    def skin(self, widget):
        options = widget.keys()
        config = {}
        if 'background' in options:
            config['background'] = theme.CARD if isinstance(widget, (tk.Entry, tk.OptionMenu)) else theme.BG
        if 'foreground' in options:
            config['foreground'] = theme.TEXT
        if 'insertbackground' in options:
            config['insertbackground'] = theme.ACCENT
        if 'font' in options:
            config['font'] = ('Segoe UI', 10)
        if isinstance(widget, tk.Button):
            config.update(background='#22314a', activebackground='#304766',
                          activeforeground=theme.TEXT, relief='flat', pady=6)
        if isinstance(widget, tk.Checkbutton):
            config.update(selectcolor=theme.CARD, activebackground=theme.BG,
                          activeforeground=theme.TEXT)
        widget.configure(**config)
        for child in widget.winfo_children():
            self.skin(child)

    def update_gui_size(self):
        # Window layout only; never touch fishing values when an option changes.
        self.root.geometry('720x270' if self.compact_mode else '720x780')

    def setup_hotkeys(self):
        core.keyboard.unhook_all()
        actions = {'start_stop': self.toggle_start_stop,
                   'change_area': self.area_button, 'exit': self.exit_app}
        for action, callback in actions.items():
            core.keyboard.add_hotkey(self.keybindings[action].lower(),
                                      lambda cb=callback: self.ui_events.put(cb))

    def refresh_hotkeys(self):
        self.setup_hotkeys()

    def rebind_key(self, action):
        self.shortcuts_dialog()

    def shortcuts_dialog(self):
        if self.is_running:
            messagebox.showinfo('Atalhos', 'Pare a pesca antes de alterar os atalhos.')
            return
        dialog = tk.Toplevel(self.root)
        dialog.title('Atalhos — não precisa de F1')
        dialog.attributes('-topmost', True)
        dialog.configure(bg=theme.BG)
        entries = {}
        for row, (action, label) in enumerate([('start_stop', 'Iniciar / parar'),
                                              ('change_area', 'Selecionar / salvar área'),
                                              ('exit', 'Encerrar')]):
            tk.Label(dialog, text=label, bg=theme.BG, fg=theme.TEXT).grid(row=row, column=0, padx=12, pady=12)
            value = tk.StringVar(value=self.keybindings[action])
            tk.Entry(dialog, textvariable=value).grid(row=row, column=1, padx=12)
            entries[action] = value
        tk.Label(dialog, text='Ex.: INSERT, HOME, END, CTRL+G ou ALT+P', bg=theme.BG,
                 fg=theme.MUTED).grid(row=3, columnspan=2, padx=12, pady=8)
        def save():
            bindings = {key: value.get().strip().upper() for key, value in entries.items()}
            try:
                parsed = [parse_shortcut(value) for value in bindings.values()]
                if len(set(parsed)) != 3:
                    raise ValueError('Use três atalhos diferentes.')
                previous = self.keybindings.copy()
                self.keybindings = bindings
                try:
                    self.refresh_hotkeys()
                except Exception:
                    self.keybindings = previous
                    self.refresh_hotkeys()
                    raise
                self.save_settings()
                dialog.destroy()
                # Original method recreates its controls with the new key labels.
                self.update_button_labels()
            except (ValueError, KeyError) as error:
                messagebox.showerror('Atalho inválido', str(error), parent=dialog)
        tk.Button(dialog, text='Salvar atalhos', command=save).grid(row=4, columnspan=2, pady=12)

    def start_delayed(self):
        if self.is_running or self.pending_start is not None or self.closing:
            return
        if self.main_thread is not None and self.main_thread.is_alive():
            self.summary.config(text='Aguarde a execução anterior encerrar antes de reiniciar.')
            return
        if self.area_selector is not None:
            self.change_area()
        self.countdown(3)

    def countdown(self, remaining):
        if remaining <= 0:
            self.pending_start = None
            self.toggle_start_stop()
            return
        self.summary.config(text=f'Iniciando em {remaining}… Volte à janela do jogo.')
        self.pending_start = self.root.after(1000, lambda: self.countdown(remaining-1))

    def stop_button(self):
        if self.pending_start is not None:
            self.root.after_cancel(self.pending_start)
            self.pending_start = None
        if self.is_running:
            self.toggle_start_stop()

    def area_button(self):
        if self.is_running:
            self.stop_button()
        self.change_area()
        if self.area_selector is not None:
            self.status_label.config(text='Mova/redimensione a área verde; clique Área novamente para salvar.')

    def toggle_compact(self):
        self.compact_mode = not self.compact_mode
        if self.compact_mode:
            self.canvas.pack_forget()
            self.scrollbar.pack_forget()
        else:
            self.canvas.pack(side='left', fill='both', expand=True)
            self.scrollbar.pack(side='right', fill='y')
        self.update_gui_size()

    def pump(self):
        while not self.ui_events.empty():
            self.ui_events.get()()
        if self.closing:
            if self.main_thread is None or not self.main_thread.is_alive():
                core.win32api.mouse_event(core.win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                core.keyboard.unhook_all()
                self.root.destroy()
                return
        if self.pending_start is None:
            state = 'Pescando' if self.is_running else 'Parado'
            self.summary.config(text=f'{state}  ·  Ciclos: {self.fish_caught_count}  ·  {self.keybindings["start_stop"]} iniciar/parar\n'
                                'Inclua o peixe branco inteiro na área. Motor e setas do arquivo original.')
        self.root.after(50, self.pump)

    def exit_app(self):
        self.stop_button()
        self.closing = True


def main():
    if sys.platform != 'win32':
        raise SystemExit('Este macro requer Windows.')
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    App(root)
    root.mainloop()
