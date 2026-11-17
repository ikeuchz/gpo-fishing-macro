import unittest
from unittest.mock import patch
from gpo_macro.language import portuguese, PortugueseMessages


class PortugueseTests(unittest.TestCase):
    def test_original_messages_are_translated(self):
        self.assertEqual(portuguese('Status: Running'), 'Status: pescando')
        self.assertEqual(portuguese('Click anywhere to set Water_2 Point...'),
                         'Clique no jogo para definir: Água após selecionar isca.')
        self.assertEqual(portuguese('Store_Fruit Point set: (10, 20)'),
                         'Guardar fruta: ponto salvo em (10, 20)')
        self.assertEqual(portuguese('Water Point 3: (30, 40)'),
                         'Água após guardar fruta: (30, 40)')

    def test_validation_dialog_uses_portuguese_without_changing_result(self):
        with patch('gpo_macro.language.messagebox.showerror', return_value='ok') as show:
            result = PortugueseMessages().showerror('Error', 'Invalid timeout value. Please enter numbers only.')
        self.assertEqual(result, 'ok')
        show.assert_called_once_with('Erro', 'Informe apenas números nos tempos de espera.')


class LanguagePreferenceTests(unittest.TestCase):
    def test_english_default_and_preference_roundtrip(self):
        import tempfile
        from pathlib import Path
        from gpo_macro.language import Translator, load_locale, save_locale
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'interface.json'
            self.assertEqual(load_locale(path), 'en')
            save_locale(path, 'pt')
            self.assertEqual(load_locale(path), 'pt')
            save_locale(path, 'en')
            self.assertEqual(load_locale(path), 'en')
            path.write_text('invalid json')
            self.assertEqual(load_locale(path), 'en')
        self.assertEqual(Translator().translate('Pesca'), 'Fishing')

    def test_static_and_live_messages_switch_both_directions(self):
        from gpo_macro.language import Translator
        translator = Translator()
        self.assertEqual(translator.translate('Salvar cores'), 'Save colors')
        self.assertEqual(translator.translate('Iniciando em 3… Volte à janela do jogo.'),
                         'Starting in 3… Switch to the game window.')
        self.assertEqual(translator.translate('Em pesca   ·   8 ciclos   ·   CTRL+G iniciar / parar'),
                         'Fishing   ·   8 cycles   ·   CTRL+G start / stop')
        self.assertEqual(translator.translate('Status: Running'), 'Status: Running')
        translator.set_locale('pt')
        self.assertEqual(translator.translate('Salvar cores'), 'Salvar cores')
        self.assertEqual(translator.translate('Status: Running'), 'Status: pescando')
        translator.set_locale('en')
        self.assertEqual(translator.translate('Salvar cores'), 'Save colors')

    def test_localized_dialog_preserves_result(self):
        from gpo_macro.language import Translator, LocalizedMessages
        translator = Translator()
        with patch('gpo_macro.language.messagebox.showinfo', return_value='ok') as show:
            self.assertEqual(LocalizedMessages(translator).showinfo('Atalhos', 'Use três atalhos diferentes.'), 'ok')
        show.assert_called_once_with('Shortcuts', 'Use three different shortcuts.')
