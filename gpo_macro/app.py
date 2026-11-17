"""Presentation adapter. Fishing methods are inherited from the original core."""
from pathlib import Path
import queue
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from .original import OriginalMacro, core
from .hotkeys import parse_shortcut
from . import theme
from .language import StatusLabel, PointButton, PortugueseMessages


class App(OriginalMacro):
    def __init__(self, root):
        self.ui_events = queue.SimpleQueue()
        self.pending_start = None
        self.compact_mode = False
        self.closing = False
        core.messagebox = PortugueseMessages()
        super().__init__(root)
        root.title('GPO Fishing — ikeuchz')
        self.full_geometry = f'720x{max(580, min(780, root.winfo_screenheight()-90))}'
        root.geometry(self.full_geometry)
        root.resizable(True, True)
        root.minsize(640, 260)
        root.attributes('-topmost', True)
        assets = Path(__file__).parent/'assets'
        if not hasattr(self, 'icon'):
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
        self.header = ttk.Frame(self.root)
        self.header.pack(fill='x', padx=24, pady=(22, 16))
        assets = Path(__file__).parent/'assets'
        if not hasattr(self, 'icon'):
            self.icon = tk.PhotoImage(file=str(assets/'app.png'))
        ttk.Label(self.header, image=self.icon).pack(side='left', padx=(0, 14))
        brand = ttk.Frame(self.header)
        brand.pack(side='left')
        ttk.Label(brand, text='GPO Fishing', style='Title.TLabel').pack(anchor='w')
        ttk.Label(brand, text='IKEUCHZ  /  PAINEL DE PESCA', style='Muted.TLabel').pack(anchor='w', pady=(3, 0))
        self.compact_control = ttk.Button(self.header, text='Modo compacto', command=self.toggle_compact)
        self.compact_control.pack(side='right')

        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill='x', padx=24, pady=(0, 12))
        ttk.Button(self.toolbar, text='▶  Iniciar pesca', style='Accent.TButton',
                   command=self.start_delayed).pack(side='left')
        ttk.Button(self.toolbar, text='■  Parar', command=self.stop_button).pack(side='left', padx=8)
        self.area_control = ttk.Button(self.toolbar, text='Selecionar área', command=self.area_button)
        self.area_control.pack(side='left')
        ttk.Button(self.toolbar, text='Atalhos', command=self.shortcuts_dialog).pack(side='right')

        self.summary = tk.Label(self.root, text='Pronto para pescar', anchor='w',
                                bg=theme.CARD, fg=theme.ACCENT, padx=16, pady=12,
                                font=('Segoe UI', 11, 'bold'))
        self.summary.pack(fill='x', padx=24, pady=(0, 14))
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=24, pady=(0, 12))
        self.tabs = {}
        self.canvases = []
        for name in ('Pesca', 'Controle', 'Automação'):
            page = ttk.Frame(self.notebook)
            self.notebook.add(page, text=name)
            canvas = tk.Canvas(page, background=theme.BG, highlightthickness=0)
            bar = ttk.Scrollbar(page, orient='vertical', command=canvas.yview)
            canvas.configure(yscrollcommand=bar.set)
            bar.pack(side='right', fill='y')
            canvas.pack(side='left', fill='both', expand=True)
            content = ttk.Frame(canvas, padding=(0, 14, 10, 8))
            window = canvas.create_window((0, 0), window=content, anchor='nw')
            content.bind('<Configure>', lambda e, c=canvas: c.configure(scrollregion=c.bbox('all')))
            canvas.bind('<Configure>', lambda e, c=canvas, w=window: c.itemconfigure(w, width=e.width))
            self.tabs[name] = content
            self.canvases.append(canvas)
        def wheel(event):
            selected = self.notebook.index(self.notebook.select())
            if str(event.widget).startswith(str(self.notebook)):
                self.canvases[selected].yview_scroll(-int(event.delta/120), 'units')
        self.root.bind('<MouseWheel>', wheel)

        def card(parent, title, description):
            frame = ttk.Frame(parent, style='Card.TFrame', padding=18)
            frame.pack(fill='both', expand=True, pady=(0, 12))
            ttk.Label(frame, text=title, style='CardTitle.TLabel').pack(anchor='w')
            hint = ttk.Label(frame, text=description, style='CardHint.TLabel', wraplength=520)
            hint.pack(anchor='w', fill='x', pady=(4, 14))
            hint.bind('<Configure>', lambda e, label=hint: label.configure(wraplength=max(150, e.width)))
            return frame

        def row(parent, label):
            frame = ttk.Frame(parent, style='Card.TFrame')
            frame.pack(fill='x', pady=5)
            ttk.Label(frame, text=label, style='Card.TLabel').pack(side='left')
            return frame

        def number(parent, label, field, value, stacked=False):
            if stacked:
                line = ttk.Frame(parent, style='Card.TFrame')
                line.pack(fill='x', pady=5)
                ttk.Label(line, text=label, style='Card.TLabel').pack(anchor='w', pady=(0, 5))
            else:
                line = row(parent, label)
            widget = ttk.Entry(line, width=16, justify='right')
            widget.insert(0, str(value))
            widget.pack(fill='x' if stacked else 'none', side='top' if stacked else 'right')
            setattr(self, field, widget)
            return widget

        def key(parent, label, field, value, stacked=False):
            if stacked:
                line = ttk.Frame(parent, style='Card.TFrame')
                line.pack(fill='x', pady=5)
                ttk.Label(line, text=label, style='Card.TLabel').pack(anchor='w', pady=(0, 5))
            else:
                line = row(parent, label)
            variable = tk.StringVar(value=str(value))
            ttk.Combobox(line, textvariable=variable, values=tuple('1234567890'),
                         state='readonly', width=13, justify='right').pack(fill='x' if stacked else 'none', side='top' if stacked else 'right')
            setattr(self, field, variable)

        def apply(parent, text, command):
            ttk.Button(parent, text=text, command=command).pack(anchor='e', pady=(12, 0))

        def point(parent, label, attr, point_name):
            line = row(parent, label)
            button = PointButton(line, text='Definir ponto', command=lambda: self.capture_point(point_name),
                                 bg='#22314a', fg=theme.TEXT, activebackground='#304766',
                                 activeforeground=theme.TEXT, relief='flat', padx=12, pady=7,
                                 cursor='hand2', font=('Segoe UI', 10))
            button.pack(side='right')
            setattr(self, attr, button)

        pesca = self.tabs['Pesca']
        twins = ttk.Frame(pesca)
        twins.pack(fill='x')
        twins.columnconfigure((0, 1), weight=1, uniform='cards')
        items_host, times_host = ttk.Frame(twins), ttk.Frame(twins)
        items_host.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        times_host.grid(row=0, column=1, sticky='nsew', padx=(6, 0))
        equipment = card(items_host, 'Itens equipados', 'Escolha as teclas dos itens no seu inventário.')
        key(equipment, 'Vara de pesca', 'rod_key_var', self.rod_key, stacked=True)
        key(equipment, 'Outro item', 'not_rod_key_var', self.not_rod_key, stacked=True)
        apply(equipment, 'Salvar itens', self.save_rod_keys)
        timing = card(times_host, 'Tempos da pesca', 'Ajuste as esperas entre as etapas do ciclo.')
        number(timing, 'Esperar fisgada (s)', 'bite_timeout_entry', self.bite_timeout, stacked=True)
        number(timing, 'Fim do minigame (s)', 'end_fish_timeout_entry', self.end_fish_timeout, stacked=True)
        apply(timing, 'Salvar tempos', self.save_timeouts)
        region = card(pesca, 'Área do minigame', 'Inclua o peixe branco inteiro na caixa verde. Clique novamente no botão para salvar a área.')
        self.area_description = ttk.Label(region, style='CardHint.TLabel')
        self.area_description.pack(anchor='w', pady=(0, 8))
        ttk.Button(region, text='Ajustar área na tela', command=self.area_button).pack(anchor='w')

        controle = self.tabs['Controle']
        precision = card(controle, 'Precisão do acompanhamento', 'Se a pesca já funciona bem, mantenha os seus valores atuais.')
        number(precision, 'Ganho proporcional (Kp)', 'kp_entry', self.kp)
        number(precision, 'Ganho derivativo (Kd)', 'kd_entry', self.kd)
        apply(precision, 'Salvar precisão', self.save_pd_gains)
        colors = card(controle, 'Detecção de cores', 'Tolerância de cada cor usada para reconhecer o minigame.')
        number(colors, 'Azul', 'blue_tolerance_entry', self.blue_tolerance)
        number(colors, 'Branco', 'white_tolerance_entry', self.white_tolerance)
        number(colors, 'Cinza', 'gray_tolerance_entry', self.gray_tolerance)
        apply(colors, 'Salvar cores', self.save_color_tolerances)

        automation = self.tabs['Automação']
        buy = card(automation, 'Compra de iscas', 'Defina os pontos do menu de compra e a frequência de reposição.')
        self.auto_buy_frame = buy
        self.auto_buy_var = tk.BooleanVar(value=self.auto_buy_bait)
        ttk.Checkbutton(buy, text='Comprar iscas automaticamente', variable=self.auto_buy_var,
                        command=self.toggle_auto_buy, style='Card.TCheckbutton').pack(anchor='w', pady=(0, 10))
        number(buy, 'Ciclos entre compras', 'loops_entry', self.loops_per_purchase)
        for label, attr, name in [('Água', 'water_btn', 'water'), ('Confirmar compra', 'yes_btn', 'yes'),
                                   ('Recusar compra', 'no_btn', 'no'), ('Quantidade de iscas', 'number_btn', 'number')]:
            point(buy, label, attr, name)
        apply(buy, 'Salvar compra de iscas', self.save_auto_buy_settings)

        store = card(automation, 'Guardar frutas', 'Configure o item e os cliques para armazenar as frutas.')
        self.auto_store_frame = store
        self.auto_store_var = tk.BooleanVar(value=self.auto_store_fruit)
        ttk.Checkbutton(store, text='Guardar frutas automaticamente', variable=self.auto_store_var,
                        command=self.toggle_auto_store, style='Card.TCheckbutton').pack(anchor='w', pady=(0, 10))
        key(store, 'Tecla da fruta', 'fruit_key_var', self.fruit_key)
        apply(store, 'Salvar tecla da fruta', self.save_fruit_key)
        point(store, 'Armazenar fruta', 'store_fruit_btn', 'store_fruit')
        point(store, 'Voltar à água', 'water_point_3_btn', 'water_3')
        apply(store, 'Salvar armazenamento', self.save_auto_store_settings)

        bait = card(automation, 'Selecionar isca', 'Marque onde escolher a isca e onde retornar à água.')
        self.auto_select_bait_frame = bait
        self.auto_select_bait_var = tk.BooleanVar(value=self.auto_select_bait)
        ttk.Checkbutton(bait, text='Selecionar isca automaticamente', variable=self.auto_select_bait_var,
                        command=self.toggle_auto_select_bait, style='Card.TCheckbutton').pack(anchor='w', pady=(0, 10))
        point(bait, 'Escolher isca', 'bait_point_btn', 'bait')
        point(bait, 'Voltar à água', 'water_point_2_btn', 'water_2')
        apply(bait, 'Salvar seleção de isca', self.save_auto_select_bait_settings)
        self.update_point_buttons()
        self.update_store_fruit_button()
        self.update_bait_point_button()
        self.update_water_point_2_button()
        self.update_water_point_3_button()

        self.status_label = StatusLabel(self.root, text='Pronto. Seus ajustes atuais foram mantidos.',
                                        bg=theme.BG, fg=theme.MUTED, anchor='w', padx=24,
                                        pady=10, font=('Segoe UI', 9), wraplength=680)
        self.status_label.pack(fill='x', side='bottom')
        self.compact_mode = False

    def update_gui_size(self):
        # Window layout only; never touch fishing values when an option changes.
        self.root.geometry('720x270' if self.compact_mode else self.full_geometry)

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
        dialog.title('Atalhos de teclado')
        dialog.attributes('-topmost', True)
        dialog.configure(bg=theme.BG)
        entries = {}
        for row, (action, label) in enumerate([('start_stop', 'Iniciar / parar'),
                                              ('change_area', 'Selecionar / salvar área'),
                                              ('exit', 'Encerrar')]):
            tk.Label(dialog, text=label, bg=theme.BG, fg=theme.TEXT).grid(row=row, column=0, padx=12, pady=12)
            value = tk.StringVar(value=self.keybindings[action])
            ttk.Entry(dialog, textvariable=value).grid(row=row, column=1, padx=12)
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
        ttk.Button(dialog, text='Salvar atalhos', command=save).grid(row=4, columnspan=2, pady=12)

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
        self.compact_control.config(text='Expandir painel' if self.compact_mode else 'Modo compacto')
        if self.compact_mode:
            self.notebook.pack_forget()
        else:
            self.notebook.pack(fill='both', expand=True, padx=24, pady=(0, 12), before=self.status_label)
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
            state = 'Em pesca' if self.is_running else 'Pronto para pescar'
            self.summary.config(text=f'{state}   ·   {self.fish_caught_count} ciclos   ·   {self.keybindings["start_stop"]} iniciar / parar')
        self.area_control.config(text='Salvar área' if self.area_selector is not None else 'Selecionar área')
        area = self.area_box
        self.area_description.config(text=f'Posição: {area["x1"]}, {area["y1"]}   ·   Tamanho: {area["x2"]-area["x1"]} × {area["y2"]-area["y1"]} pixels')
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
