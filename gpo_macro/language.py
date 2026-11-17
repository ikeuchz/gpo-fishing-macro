"""Portuguese presentation strings for messages produced by the original engine."""
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


class TranslatedText:
    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            cnf = dict(cnf)
            if 'text' in cnf:
                cnf['text'] = portuguese(cnf['text'])
        if 'text' in kwargs:
            kwargs['text'] = portuguese(kwargs['text'])
        return super().configure(cnf, **kwargs)
    config = configure


class StatusLabel(TranslatedText, tk.Label):
    pass


class PointButton(TranslatedText, tk.Button):
    pass


class PortugueseMessages:
    def __getattr__(self, name):
        original = getattr(messagebox, name)
        def show(title=None, message=None, **kwargs):
            return original(portuguese(title), portuguese(message), **kwargs)
        return show
