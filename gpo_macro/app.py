import json
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .config import Settings
from .engine import Engine
from .windows import WindowsInput
from .hotkeys import active_shortcuts
from . import theme
from .overlay import TrackingOverlay


class App:
    def __init__(self, root):
        self.root = root
        root.title('GPO Fishing Macro — ikeuchz')
        root.geometry('820x820')
        root.minsize(700, 600)
        theme.apply(root)
        root.attributes('-topmost', True)
        assets = Path(__file__).resolve().parent / 'assets'
        icon = assets / 'app.ico'
        if sys.platform == 'win32' and icon.exists():
            root.iconbitmap(str(icon))
        png = assets / 'app.png'
        if png.exists():
            self.icon = tk.PhotoImage(file=str(png))
            root.iconphoto(True, self.icon)
        self.path = (Path(sys.executable).parent if getattr(sys, 'frozen', False)
                     else Path(__file__).resolve().parent.parent) / 'settings.json'
        self.inputs = WindowsInput()
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.worker = None
        self.selecting = False
        self.closing = False
        self.capture_pending = False
        self.keys = set()
        self.start_pending = None
        self.overlay = None
        self.overlay_area = None
        self.observations = queue.Queue(maxsize=1)
        self.compact_mode = False
        try:
            self.settings = Settings.load(self.path)
        except (ValueError, TypeError, OSError, KeyError) as error:
            messagebox.showwarning('Configuração', f'Não foi possível carregar as configurações:\n{error}')
            self.settings = Settings()
        header = ttk.Frame(root)
        self.header = header
        header.pack(fill='x', padx=24, pady=(22, 16))
        if hasattr(self, 'icon'):
            ttk.Label(header, image=self.icon).pack(side='left', padx=(0, 15))
        heading = ttk.Frame(header)
        heading.pack(side='left')
        ttk.Label(heading, text='GPO Fishing', style='Title.TLabel').pack(anchor='w')
        ttk.Label(heading, text='IKEUCHZ  /  PESCA E AUTOMAÇÃO', style='Muted.TLabel').pack(anchor='w')
        self.status = tk.StringVar(value='Pronto para configurar sua próxima sessão.')
        ttk.Label(root, textvariable=self.status, style='Status.TLabel', wraplength=720).pack(fill='x', padx=24, pady=(0, 12))
        controls = ttk.Frame(root)
        controls.pack(fill='x', padx=24, pady=(0, 8))
        ttk.Button(controls, text='▶  Iniciar em 3 segundos', style='Accent.TButton', command=self.start_from_button).pack(side='left')
        ttk.Button(controls, text='■  Parar / cancelar', command=self.stop_from_button).pack(side='left', padx=8)
        ttk.Button(controls, text='Selecionar área', command=self.select_area).pack(side='right')
        view = ttk.Frame(root)
        view.pack(fill='x', padx=24, pady=(0, 8))
        self.on_top = tk.BooleanVar(value=True)
        ttk.Checkbutton(view, text='Sempre visível', variable=self.on_top,
                        command=lambda: root.attributes('-topmost', self.on_top.get())).pack(side='left')
        ttk.Button(view, text='Modo compacto / completo', command=self.toggle_compact).pack(side='right')
        self.shortcut_hint = tk.StringVar()
        ttk.Label(root, textvariable=self.shortcut_hint, style='Muted.TLabel').pack(anchor='w', padx=24, pady=(0, 10))
        self.update_shortcut_hint()
        notebook = ttk.Notebook(root)
        self.notebook = notebook
        notebook.pack(fill='both', expand=True, padx=12, pady=10)
        page = ttk.Frame(notebook)
        notebook.add(page, text='Configurações de pesca')
        viewport = tk.Canvas(page, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient='vertical', command=viewport.yview)
        viewport.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        viewport.pack(side='left', fill='both', expand=True)
        main = ttk.Frame(viewport)
        window = viewport.create_window((0, 0), window=main, anchor='nw')
        main.bind('<Configure>', lambda e: viewport.configure(scrollregion=viewport.bbox('all')))
        viewport.bind('<Configure>', lambda e: viewport.itemconfigure(window, width=e.width))
        def wheel(event):
            if str(event.widget).startswith(str(page)):
                viewport.yview_scroll(-int(event.delta / 120), 'units')
        root.bind('<MouseWheel>', wheel, add='+')
        self.fields = {}
        fields = [('control_bar', 'Barra de controle: left / right'), ('area', 'Área: x, y, largura, altura'), ('rod_key', 'Tecla da vara'),
                  ('other_key', 'Tecla de outro item'), ('bite_timeout', 'Espera pela fisgada (s)'),
                  ('end_timeout', 'Espera para concluir ciclo (s)'), ('cast_hold', 'Duração do lançamento (s)'),
                  ('interval', 'Intervalo de captura (s)'), ('kp', 'Ganho proporcional'),
                  ('kd', 'Ganho derivativo por quadro'), ('blue_tolerance', 'Tolerância azul'),
                  ('white_tolerance', 'Tolerância branco'), ('gray_tolerance', 'Tolerância cinza'),
                  ('foreground_title', 'Parte do título da janela do jogo'), ('buy_every', 'Comprar a cada N ciclos')]
        for row, (name, label) in enumerate(fields):
            ttk.Label(main, text=label).grid(row=row, column=0, sticky='w', padx=8, pady=4)
            value = getattr(self.settings, name)
            variable = tk.StringVar(value=', '.join(map(str, value)) if name == 'area' else str(value))
            self.fields[name] = variable
            ttk.Entry(main, textvariable=variable, width=25).grid(row=row, column=1, sticky='ew', padx=8)
        main.columnconfigure(1, weight=1)
        ttk.Button(main, text='Selecionar área na tela', command=self.select_area).grid(row=len(fields), column=0, pady=10)
        shortcuts = ttk.Frame(notebook)
        notebook.add(shortcuts, text='Atalhos')
        ttk.Label(shortcuts, text='Escolha as teclas que existem no seu teclado.', font=('Segoe UI', 13, 'bold')).pack(anchor='w', padx=18, pady=(20, 10))
        ttk.Label(shortcuts, text='Exemplos: INSERT, HOME, END, CTRL+G, ALT+P ou F1.\nSalve para aplicar. Não é necessário usar teclas F.', style='Muted.TLabel').pack(anchor='w', padx=18, pady=(0, 18))
        for name, label in [('start_hotkey', 'Iniciar / parar'), ('area_hotkey', 'Selecionar área'), ('exit_hotkey', 'Encerrar aplicativo')]:
            row = ttk.Frame(shortcuts)
            row.pack(fill='x', padx=18, pady=8)
            ttk.Label(row, text=label, width=25).pack(side='left')
            variable = tk.StringVar(value=getattr(self.settings, name))
            self.fields[name] = variable
            ttk.Entry(row, textvariable=variable, width=25).pack(side='left')
        advanced = ttk.Frame(notebook)
        notebook.add(advanced, text='Rotinas e pontos')
        self.toggles = {}
        for name, label in [('auto_cast', 'Lançar vara automaticamente (opcional)'), ('auto_buy', 'Comprar iscas'), ('auto_bait', 'Selecionar isca'), ('auto_store', 'Guardar fruta')]:
            variable = tk.BooleanVar(value=getattr(self.settings, name))
            self.toggles[name] = variable
            ttk.Checkbutton(advanced, text=label, variable=variable).pack(anchor='w', padx=8, pady=4)
        ttk.Label(advanced, text='Capture pontos e edite as ações em JSON: click, key ou wait.', wraplength=600).pack(padx=8, pady=8)
        ttk.Button(advanced, text='Capturar ponto em 3 segundos', command=self.capture_point).pack(pady=6)
        ttk.Label(advanced, text='Lançamento automático desligado: apenas acompanha o minigame.', style='Muted.TLabel').pack(padx=8, pady=4)
        self.editor = tk.Text(advanced, height=14, width=65, undo=True, bg=theme.CARD, fg=theme.TEXT, insertbackground=theme.ACCENT, selectbackground='#304766', relief='flat', padx=12, pady=12, font=('Consolas', 10))
        self.editor.pack(fill='both', expand=True, padx=8, pady=8)
        self.editor.insert('1.0', json.dumps({'points': self.settings.points, 'routines': self.settings.routines}, indent=2))
        self.footer = ttk.Frame(root)
        self.footer.pack(pady=(0, 10))
        ttk.Button(self.footer, text='Salvar configurações', command=self.save).pack()
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(50, self.poll)

    def read_settings(self):
        data = {name: variable.get() for name, variable in self.fields.items()}
        data['area'] = [int(v.strip()) for v in data['area'].split(',')]
        for name in ('blue_tolerance', 'white_tolerance', 'gray_tolerance', 'buy_every'):
            data[name] = int(data[name])
        for name in ('bite_timeout', 'end_timeout', 'cast_hold', 'interval', 'kp', 'kd'):
            data[name] = float(data[name])
        data.update({name: variable.get() for name, variable in self.toggles.items()})
        extra = json.loads(self.editor.get('1.0', 'end'))
        if set(extra) != {'points', 'routines'}:
            raise ValueError('O JSON deve conter points e routines.')
        data.update(extra)
        return Settings(**data).validate()

    def save(self):
        try:
            self.settings = self.read_settings()
            self.settings.save(self.path)
            if not self.busy():
                self.show_overlay(self.settings.area)
            self.update_shortcut_hint()
            self.status.set(f'Salvo. Volte ao jogo e use {self.settings.start_hotkey}, ou o botão Iniciar.')
            return True
        except (ValueError, TypeError, OSError, KeyError, AttributeError) as error:
            messagebox.showerror('Configuração', str(error))
            return False

    def toggle_compact(self):
        self.compact_mode = not self.compact_mode
        if self.compact_mode:
            self.full_geometry = self.root.geometry()
            self.header.pack_forget()
            self.notebook.pack_forget()
            self.footer.pack_forget()
            self.root.minsize(700, 220)
            self.root.geometry('760x250')
        else:
            self.header.pack(fill='x', padx=24, pady=(22, 16), before=self.root.winfo_children()[1])
            self.notebook.pack(fill='both', expand=True, padx=12, pady=10)
            self.footer.pack(pady=(0, 10))
            self.root.minsize(700, 600)
            self.root.geometry(self.full_geometry)

    def show_overlay(self, area):
        if sys.platform != 'win32':
            return
        if self.overlay is not None and self.overlay_area != area:
            self.overlay.close()
            self.overlay = None
        if self.overlay is None:
            self.overlay = TrackingOverlay(self.root, self.inputs, list(area))
            self.overlay_area = list(area)

    def observe(self, target):
        # Worker only publishes data; Tk painting stays on the UI thread.
        try:
            self.observations.get_nowait()
        except queue.Empty:
            pass
        try:
            self.observations.put_nowait(target)
        except queue.Full:
            pass

    def update_shortcut_hint(self):
        self.shortcut_hint.set(f'{self.settings.start_hotkey} iniciar/parar    ·    {self.settings.area_hotkey} área    ·    {self.settings.exit_hotkey} sair')

    def start_from_button(self):
        if self.busy() or self.selecting or self.capture_pending or self.start_pending is not None:
            return
        if not self.save():
            return
        self.countdown(3)

    def countdown(self, remaining):
        if self.closing:
            return
        if remaining == 0:
            self.start_pending = None
            self.toggle()
            return
        self.status.set(f'Iniciando em {remaining}… Clique na janela do jogo agora.')
        self.start_pending = self.root.after(1000, lambda: self.countdown(remaining-1))

    def stop_from_button(self):
        if self.start_pending is not None:
            self.root.after_cancel(self.start_pending)
            self.start_pending = None
        self.stop.set()
        self.status.set('Parando…' if self.busy() else 'Parado. Nenhuma tecla F é necessária para iniciar.')

    def busy(self):
        return self.worker is not None and self.worker.is_alive()

    def toggle(self):
        if self.busy():
            self.stop.set()
            self.status.set('Parando…')
            return
        if self.start_pending is not None:
            self.stop_from_button()
            return
        if self.selecting or self.capture_pending:
            return
        if not self.inputs.focused(self.fields['foreground_title'].get()):
            self.status.set('Início cancelado: coloque o jogo em primeiro plano e tente novamente.')
            return
        if not self.save():
            return
        self.stop = threading.Event()
        settings = self.settings
        self.show_overlay(settings.area)
        def task():
            try:
                import mss
                import numpy as np
                x, y, width, height = settings.area
                monitor = {'left': x, 'top': y, 'width': width, 'height': height}
                with mss.mss() as screen:
                    Engine(settings, self.inputs, self.stop, self.events.put, observe=self.observe).run(
                        lambda: np.asarray(screen.grab(monitor)))
            except Exception as error:
                self.events.put(f'Erro: {error}')
            finally:
                self.inputs.hold(False)
        self.worker = threading.Thread(target=task, daemon=True)
        self.worker.start()

    def select_area(self):
        if self.busy() or self.selecting or self.capture_pending or self.start_pending is not None:
            self.status.set('Pare o macro antes de selecionar a área.')
            return
        if self.overlay is not None:
            self.overlay.close()
            self.overlay = None
        self.selecting = True
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)
        overlay.attributes('-alpha', .4)
        overlay.configure(bg='black', cursor='crosshair')
        canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        canvas.create_text(20, 20, anchor='nw', text='Selecione as barras. Controle à esquerda por padrão (left). Esc cancela.', fill='white')
        anchor = []
        rectangle = [None]
        def finish(event=None):
            overlay.destroy()
            self.selecting = False
        def begin(event):
            anchor[:] = [event.x, event.y]
            if rectangle[0] is not None:
                canvas.delete(rectangle[0])
            rectangle[0] = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='lime', width=3)
        def drag(event):
            if anchor:
                canvas.coords(rectangle[0], *anchor, event.x, event.y)
        def end(event):
            if not anchor:
                return
            x, y = min(anchor[0], event.x), min(anchor[1], event.y)
            width, height = abs(event.x-anchor[0]), abs(event.y-anchor[1])
            if width >= 10 and height >= 10:
                area = [x + overlay.winfo_rootx(), y + overlay.winfo_rooty(), width, height]
                self.fields['area'].set(', '.join(map(str, area)))
                finish()
                self.show_overlay(area)
                self.status.set('Área selecionada. Salve. Branco = peixe; verde-água = seu marcador.')
        canvas.bind('<Button-1>', begin)
        canvas.bind('<B1-Motion>', drag)
        canvas.bind('<ButtonRelease-1>', end)
        overlay.bind('<Escape>', finish)
        overlay.protocol('WM_DELETE_WINDOW', finish)
        overlay.focus_force()

    def capture_point(self):
        if self.busy() or self.selecting or self.capture_pending or self.start_pending is not None:
            return
        name = simpledialog.askstring('Ponto', 'Nome do ponto (ex.: bait, water, shop, confirm, store):')
        if not name or not name.strip():
            return
        self.capture_pending = True
        self.status.set('Posicione o cursor no ponto desejado. Captura em 3 segundos…')
        def capture():
            try:
                data = json.loads(self.editor.get('1.0', 'end'))
                data['points'][name.strip()] = self.inputs.position()
                self.editor.delete('1.0', 'end')
                self.editor.insert('1.0', json.dumps(data, indent=2))
                self.status.set(f'Ponto {name.strip()} capturado. Salve as configurações.')
            except (ValueError, TypeError, KeyError) as error:
                messagebox.showerror('Ponto', str(error))
            finally:
                self.capture_pending = False
        self.root.after(3000, capture)

    def poll(self):
        try:
            target = self.observations.get_nowait()
            if self.overlay is not None:
                self.overlay.update(target)
        except queue.Empty:
            pass
        while True:
            try:
                self.status.set(self.events.get_nowait())
            except queue.Empty:
                break
        if self.closing:
            if not self.busy():
                if self.overlay is not None:
                    self.overlay.close()
                    self.overlay = None
                self.root.destroy()
                return
        else:
            bindings = {'start': self.settings.start_hotkey, 'area': self.settings.area_hotkey, 'exit': self.settings.exit_hotkey}
            down = active_shortcuts(bindings, self.inputs.down)
            pressed = down - self.keys
            self.keys = down
            if 'exit' in pressed:
                self.close()
            elif 'start' in pressed:
                self.toggle()
            elif 'area' in pressed:
                self.select_area()
        self.root.after(50, self.poll)

    def close(self):
        self.closing = True
        if self.start_pending is not None:
            self.root.after_cancel(self.start_pending)
            self.start_pending = None
        self.stop.set()
        self.status.set('Encerrando…')


def main():
    if sys.platform != 'win32':
        raise SystemExit('A interface e a automação requerem Windows.')
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    App(root)
    root.mainloop()
