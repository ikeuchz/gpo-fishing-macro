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
