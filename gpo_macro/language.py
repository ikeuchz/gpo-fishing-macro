"""English and Portuguese presentation, independent of the original fishing engine."""
import re
import tkinter as tk
from tkinter import messagebox

MESSAGES = {
    'Status: Running': 'Status: pescando', 'Status: Stopped': 'Status: parado',
    'Timeouts saved!': 'Tempos de espera salvos.', 'Rod keys saved!': 'Teclas dos itens salvas.',
    'Fruit key saved!': 'Tecla da fruta salva.', 'PD gains saved!': 'Precisão do controle salva.',
    'Color tolerances saved!': 'Tolerâncias de cor salvas.', 'Area saved!': 'Área de pesca salva.',
    'Auto buy settings saved!': 'Compra de iscas configurada.',
    'Auto Store settings saved!': 'Armazenamento de frutas configurado.',
    'Auto Select Bait settings saved!': 'Seleção de iscas configurada.',
    'Drag area box (Press F2 to save)': 'Mova a área verde e clique em Área para salvar.',
    'Invalid timeout value. Please enter numbers only.': 'Informe apenas números nos tempos de espera.',
    'Invalid PD gain value. Please enter numbers only.': 'Informe apenas números nos ganhos do controle.',
    'Invalid tolerance value. Please enter integers only.': 'Informe números inteiros nas tolerâncias de cor.',
    'Invalid loops value. Please enter a number.': 'Informe um número inteiro para os ciclos por compra.',
    'Please set both store fruit point and water point 3 before saving.':
        'Configure os pontos de guardar fruta e de retorno à água antes de salvar.',
    'Please set both bait point and water point 2 before saving.':
        'Configure os pontos de selecionar isca e de retorno à água antes de salvar.',
    'Error': 'Erro', 'Warning': 'Atenção', 'Settings': 'Configurações',
}
POINTS = {'Water': 'Água', 'Yes': 'Confirmar compra', 'No': 'Recusar compra',
          'Number': 'Quantidade', 'Store Fruit': 'Guardar fruta', 'Bait': 'Selecionar isca',
          'Water 2': 'Água após selecionar isca', 'Water 3': 'Água após guardar fruta',
          'Water_2': 'Água após selecionar isca', 'Water_3': 'Água após guardar fruta',
          'Store_Fruit': 'Guardar fruta'}


def portuguese(text):
    if not isinstance(text, str):
        return text
    if text in MESSAGES:
        return MESSAGES[text]
    for prefix, translated in [('Could not save settings: ', 'Não foi possível salvar: '),
                               ('Could not load settings: ', 'Não foi possível carregar as configurações: ')]:
        if text.startswith(prefix):
            return translated + text[len(prefix):].replace('\nUsing defaults.', '\nUsando os valores padrão.')
    for prefix, label in [('Water Point 2: ', POINTS['Water 2']), ('Water Point 3: ', POINTS['Water 3']),
                          ('Store Fruit Point: ', POINTS['Store Fruit']), ('Bait Point: ', POINTS['Bait']),
                          ('Water Point: ', POINTS['Water']), ('Yes Point: ', POINTS['Yes']),
                          ('No Point: ', POINTS['No']), ('Number Point: ', POINTS['Number'])]:
        if text.startswith(prefix):
            return f'{label}: ' + text[len(prefix):].replace('Not Set', 'não definido')
    capture = re.fullmatch(r'Click anywhere to set (.+) Point\.\.\.', text)
    if capture:
        return f'Clique no jogo para definir: {POINTS.get(capture[1], capture[1])}.'
    captured = re.fullmatch(r'(.+) Point set: (.+)', text)
    if captured:
        return f'{POINTS.get(captured[1], captured[1])}: ponto salvo em {captured[2]}'
    return text


class PortugueseMessages:
    def __getattr__(self, name):
        original = getattr(messagebox, name)
        def show(title=None, message=None, **kwargs):
            return original(portuguese(title), portuguese(message), **kwargs)
        return show

# Interface keys remain stable; changing language never rebuilds input controls.
ENGLISH = {
    'IKEUCHZ  /  PAINEL DE PESCA': 'IKEUCHZ  /  FISHING DASHBOARD',
    'Modo compacto': 'Compact mode', 'Expandir painel': 'Expand panel',
    '▶  Iniciar pesca': '▶  Start fishing', '■  Parar': '■  Stop',
    'Selecionar área': 'Select area', 'Salvar área': 'Save area', 'Atalhos': 'Shortcuts',
    'Pronto para pescar': 'Ready to fish', 'Pesca': 'Fishing', 'Controle': 'Control',
    'Automação': 'Automation', 'Itens equipados': 'Equipped items',
    'Escolha as teclas dos itens no seu inventário.': 'Choose the keys for the items in your inventory.',
    'Vara de pesca': 'Fishing rod', 'Outro item': 'Other item', 'Salvar itens': 'Save items',
    'Tempos da pesca': 'Fishing timing',
    'Ajuste as esperas entre as etapas do ciclo.': 'Adjust the waiting times between fishing stages.',
    'Esperar fisgada (s)': 'Wait for bite (s)', 'Fim do minigame (s)': 'Minigame end (s)',
    'Salvar tempos': 'Save timing', 'Área do minigame': 'Minigame area',
    'Inclua o peixe branco inteiro na caixa verde. Clique novamente no botão para salvar a área.':
        'Include the entire white fish inside the green box. Click the button again to save the area.',
    'Ajustar área na tela': 'Adjust area on screen',
    'Precisão do acompanhamento': 'Tracking precision',
    'Se a pesca já funciona bem, mantenha os seus valores atuais.':
        'If fishing already works well, keep your current values.',
    'Ganho proporcional (Kp)': 'Proportional gain (Kp)',
    'Ganho derivativo (Kd)': 'Derivative gain (Kd)', 'Salvar precisão': 'Save precision',
    'Detecção de cores': 'Color detection',
    'Tolerância de cada cor usada para reconhecer o minigame.':
        'Tolerance for each color used to detect the minigame.',
    'Azul': 'Blue', 'Branco': 'White', 'Cinza': 'Gray', 'Salvar cores': 'Save colors',
    'Compra de iscas': 'Buy bait',
    'Defina os pontos do menu de compra e a frequência de reposição.':
        'Set the purchase menu points and how often bait is replenished.',
    'Comprar iscas automaticamente': 'Buy bait automatically', 'Ciclos entre compras': 'Cycles between purchases',
    'Água': 'Water', 'Confirmar compra': 'Confirm purchase', 'Recusar compra': 'Decline purchase',
    'Quantidade de iscas': 'Bait quantity', 'Definir ponto': 'Set point',
    'Salvar compra de iscas': 'Save bait purchase', 'Guardar frutas': 'Store fruits',
    'Configure o item e os cliques para armazenar as frutas.':
        'Set the item key and click points used to store fruits.',
    'Guardar frutas automaticamente': 'Store fruits automatically', 'Tecla da fruta': 'Fruit key',
    'Salvar tecla da fruta': 'Save fruit key', 'Armazenar fruta': 'Store fruit',
    'Voltar à água': 'Return to water', 'Salvar armazenamento': 'Save fruit storage',
    'Selecionar isca': 'Select bait',
    'Marque onde escolher a isca e onde retornar à água.':
        'Mark where to select bait and where to return to the water.',
    'Selecionar isca automaticamente': 'Select bait automatically', 'Escolher isca': 'Choose bait',
    'Salvar seleção de isca': 'Save bait selection',
    'Pronto. Seus ajustes atuais foram mantidos.': 'Ready. Your existing settings have been kept.',
    'Atalhos de teclado': 'Keyboard shortcuts', 'Iniciar / parar': 'Start / stop',
    'Selecionar / salvar área': 'Select / save area', 'Encerrar': 'Exit',
    'Ex.: INSERT, HOME, END, CTRL+G ou ALT+P': 'Examples: INSERT, HOME, END, CTRL+G or ALT+P',
    'Salvar atalhos': 'Save shortcuts', 'Use três atalhos diferentes.': 'Use three different shortcuts.',
    'Atalho inválido': 'Invalid shortcut',
    'Pare a pesca antes de alterar os atalhos.': 'Stop fishing before changing shortcuts.',
    'Aguarde a execução anterior encerrar antes de reiniciar.': 'Wait for the previous session to finish before restarting.',
    'Mova/redimensione a área verde; clique Área novamente para salvar.':
        'Move or resize the green area, then click Save area to confirm.',
    'Atalho deve ser um texto.': 'A shortcut must be text.',
    'Informe um atalho, por exemplo INSERT ou CTRL+G.': 'Enter a shortcut, such as INSERT or CTRL+G.',
    'Use CTRL, ALT ou SHIFT antes da tecla.': 'Use CTRL, ALT or SHIFT before the key.',
    'Use INSERT, HOME, END, PAGEUP, PAGEDOWN, PAUSE, F1–F12 ou uma letra/número com modificador.':
        'Use INSERT, HOME, END, PAGEUP, PAGEDOWN, PAUSE, F1–F12 or a letter/number with a modifier.',
    'Idioma': 'Language', 'Erro': 'Error', 'Atenção': 'Warning',
}


def english(text):
    if not isinstance(text, str):
        return text
    if text in ENGLISH:
        return ENGLISH[text]
    # Engine strings are already English. Reverse known Portuguese messages as
    # well so a visible confirmation remains correct during an instant switch.
    reverse = {value: key for key, value in MESSAGES.items()}
    if text in reverse:
        return reverse[text]
    countdown = re.fullmatch(r'Iniciando em (\d+)… Volte à janela do jogo\.', text)
    if countdown:
        return f'Starting in {countdown[1]}… Switch to the game window.'
    state = re.fullmatch(r'(Pronto para pescar|Em pesca)   ·   (\d+) ciclos   ·   (.+) iniciar / parar', text)
    if state:
        label = 'Fishing' if state[1] == 'Em pesca' else 'Ready to fish'
        return f'{label}   ·   {state[2]} cycles   ·   {state[3]} start / stop'
    area = re.fullmatch(r'Posição: (.+)   ·   Tamanho: (.+) pixels', text)
    if area:
        return f'Position: {area[1]}   ·   Size: {area[2]} pixels'
    prefix = 'Não foi possível salvar o idioma: '
    if text.startswith(prefix):
        return 'Could not save the language preference: ' + text[len(prefix):]
    return text


class Translator:
    def __init__(self, locale='en'):
        import weakref
        self.locale = locale if locale in ('en', 'pt') else 'en'
        self.widgets = weakref.WeakSet()
        self.titles = weakref.WeakKeyDictionary()

    def translate(self, text):
        return portuguese(text) if self.locale == 'pt' else english(text)

    def set_locale(self, locale):
        if locale not in ('en', 'pt'):
            raise ValueError('Unsupported interface language')
        self.locale = locale
        for widget in list(self.widgets):
            if widget.winfo_exists():
                widget.refresh_language()
        for window, title in list(self.titles.items()):
            if window.winfo_exists():
                window.title(self.translate(title))

    def bind_title(self, window, title):
        self.titles[window] = title
        window.title(self.translate(title))


def load_locale(path):
    import json
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        locale = value.get('language')
        return locale if locale in ('en', 'pt') else 'en'
    except (OSError, ValueError, TypeError, AttributeError):
        return 'en'


def save_locale(path, locale):
    import json
    from pathlib import Path
    if locale not in ('en', 'pt'):
        raise ValueError('Unsupported interface language')
    temporary = Path(str(path) + '.tmp')
    temporary.write_text(json.dumps({'language': locale}, indent=2), encoding='utf-8')
    temporary.replace(path)


class LocalizedText:
    def __init__(self, *args, translator, **kwargs):
        self.translator = translator
        self.source_text = kwargs.get('text', '')
        if 'text' in kwargs:
            kwargs['text'] = translator.translate(kwargs['text'])
        super().__init__(*args, **kwargs)
        translator.widgets.add(self)

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            cnf = dict(cnf)
            if 'text' in cnf:
                self.source_text = cnf['text']
                cnf['text'] = self.translator.translate(cnf['text'])
        if 'text' in kwargs:
            self.source_text = kwargs['text']
            kwargs['text'] = self.translator.translate(kwargs['text'])
        return super().configure(cnf, **kwargs)
    config = configure

    def refresh_language(self):
        self.configure(text=self.source_text)


from tkinter import ttk


class LocalizedLabel(LocalizedText, ttk.Label): pass
class LocalizedButton(LocalizedText, ttk.Button): pass
class LocalizedCheckbutton(LocalizedText, ttk.Checkbutton): pass
class LocalizedTkLabel(LocalizedText, tk.Label): pass
class LocalizedPointButton(LocalizedText, tk.Button): pass


class LocalizedWidgets:
    def __init__(self, translator):
        self.translator = translator

    def Label(self, *args, **kwargs):
        return LocalizedLabel(*args, translator=self.translator, **kwargs)

    def Button(self, *args, **kwargs):
        return LocalizedButton(*args, translator=self.translator, **kwargs)

    def Checkbutton(self, *args, **kwargs):
        return LocalizedCheckbutton(*args, translator=self.translator, **kwargs)

    def tk_label(self, *args, **kwargs):
        return LocalizedTkLabel(*args, translator=self.translator, **kwargs)

    def point_button(self, *args, **kwargs):
        return LocalizedPointButton(*args, translator=self.translator, **kwargs)


class LocalizedMessages:
    def __init__(self, translator):
        self.translator = translator

    def __getattr__(self, name):
        original = getattr(messagebox, name)
        def show(title=None, message=None, **kwargs):
            return original(self.translator.translate(title), self.translator.translate(message), **kwargs)
        return show
