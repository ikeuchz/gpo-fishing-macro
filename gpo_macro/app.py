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


class App:
    def __init__(self, root):
        self.root = root
        root.title('GPO Fishing Macro — ikeuchz')
        root.geometry('660x720')
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
        try:
            self.settings = Settings.load(self.path)
        except (ValueError, TypeError, OSError, KeyError) as error:
            messagebox.showwarning('Configuração', f'Não foi possível carregar as configurações:\n{error}')
            self.settings = Settings()
        self.status = tk.StringVar(value='Configure a área. Com o jogo em foco, pressione F1.')
        ttk.Label(root, textvariable=self.status, wraplength=630).pack(padx=12, pady=10)
        ttk.Label(root, text='F1 iniciar/parar · F2 selecionar área · F3 encerrar').pack()
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=12, pady=10)
        main = ttk.Frame(notebook)
        notebook.add(main, text='Pesca')
        self.fields = {}
        fields = [('area', 'Área: x, y, largura, altura'), ('rod_key', 'Tecla da vara'),
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
        ttk.Button(main, text='Selecionar área (F2)', command=self.select_area).grid(row=len(fields), column=0, pady=10)
        advanced = ttk.Frame(notebook)
        notebook.add(advanced, text='Rotinas e pontos')
        self.toggles = {}
        for name, label in [('auto_buy', 'Comprar iscas'), ('auto_bait', 'Selecionar isca'), ('auto_store', 'Guardar fruta')]:
            variable = tk.BooleanVar(value=getattr(self.settings, name))
            self.toggles[name] = variable
            ttk.Checkbutton(advanced, text=label, variable=variable).pack(anchor='w', padx=8, pady=4)
        ttk.Label(advanced, text='Capture pontos e edite as ações em JSON: click, key ou wait.', wraplength=600).pack(padx=8, pady=8)
        ttk.Button(advanced, text='Capturar ponto em 3 segundos', command=self.capture_point).pack(pady=6)
        self.editor = tk.Text(advanced, height=19, width=65, undo=True)
        self.editor.pack(fill='both', expand=True, padx=8, pady=8)
        self.editor.insert('1.0', json.dumps({'points': self.settings.points, 'routines': self.settings.routines}, indent=2))
        ttk.Button(root, text='Salvar configurações', command=self.save).pack(pady=(0, 10))
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
            self.status.set('Configurações salvas. Volte ao jogo e pressione F1.')
            return True
        except (ValueError, TypeError, OSError, KeyError, AttributeError) as error:
            messagebox.showerror('Configuração', str(error))
            return False

    def busy(self):
        return self.worker is not None and self.worker.is_alive()

    def toggle(self):
        if self.busy():
            self.stop.set()
            self.status.set('Parando…')
            return
        if self.selecting or self.capture_pending:
            return
        if not self.inputs.focused(self.fields['foreground_title'].get()):
            self.status.set('Coloque a janela do jogo em primeiro plano antes de pressionar F1.')
            return
        if not self.save():
            return
        self.stop = threading.Event()
        settings = self.settings
        def task():
            try:
                import mss
                import numpy as np
                x, y, width, height = settings.area
                monitor = {'left': x, 'top': y, 'width': width, 'height': height}
                with mss.mss() as screen:
                    Engine(settings, self.inputs, self.stop, self.events.put).run(
                        lambda: np.asarray(screen.grab(monitor)))
            except Exception as error:
                self.events.put(f'Erro: {error}')
            finally:
                self.inputs.hold(False)
        self.worker = threading.Thread(target=task, daemon=True)
        self.worker.start()

    def select_area(self):
        if self.busy() or self.selecting or self.capture_pending:
            self.status.set('Pare o macro antes de selecionar a área.')
            return
        self.selecting = True
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)
        overlay.attributes('-alpha', .4)
        overlay.configure(bg='black', cursor='crosshair')
        canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        canvas.create_text(20, 20, anchor='nw', text='Arraste sobre o minigame · Esc cancela', fill='white')
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
                self.fields['area'].set(f'{x + overlay.winfo_rootx()}, {y + overlay.winfo_rooty()}, {width}, {height}')
                finish()
                self.status.set('Área selecionada. Salve as configurações.')
        canvas.bind('<Button-1>', begin)
        canvas.bind('<B1-Motion>', drag)
        canvas.bind('<ButtonRelease-1>', end)
        overlay.bind('<Escape>', finish)
        overlay.protocol('WM_DELETE_WINDOW', finish)
        overlay.focus_force()

    def capture_point(self):
        if self.busy() or self.selecting or self.capture_pending:
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
        while True:
            try:
                self.status.set(self.events.get_nowait())
            except queue.Empty:
                break
        if self.closing:
            if not self.busy():
                self.root.destroy()
                return
        else:
            down = {code for code in (0x70, 0x71, 0x72) if self.inputs.down(code)}
            pressed = down - self.keys
            self.keys = down
            # Exit/stop has priority over selection/start.
            if 0x72 in pressed:
                self.close()
            elif 0x70 in pressed:
                self.toggle()
            elif 0x71 in pressed:
                self.select_area()
        self.root.after(50, self.poll)

    def close(self):
        self.closing = True
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
