import tempfile
from pathlib import Path
import unittest
from gpo_macro.hotkeys import parse_shortcut, active_shortcuts
from gpo_macro.config import Settings


class HotkeyTests(unittest.TestCase):
    def test_defaults_work_without_function_keys(self):
        self.assertEqual(parse_shortcut(Settings().start_hotkey)[0], 0x2D)
        self.assertEqual(parse_shortcut(' ctrl + g '), (ord('G'), frozenset({0x11})))

    def test_invalid_and_duplicate_shortcuts(self):
        for text in ('', 'G', 'CTRL+', 'CTRL+CTRL+G', 'DELETE', 'F13'):
            with self.assertRaises(ValueError): parse_shortcut(text)
        with self.assertRaises(ValueError): Settings(start_hotkey='HOME').validate()

    def test_exact_modifiers(self):
        bindings = {'plain': 'HOME', 'modified': 'CTRL+HOME'}
        self.assertEqual(active_shortcuts(bindings, {0x11,0x24}.__contains__), {'modified'})
        self.assertEqual(active_shortcuts(bindings, {0x24}.__contains__), {'plain'})

    def test_saved_shortcuts_and_old_config_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'settings.json'
            Settings(start_hotkey='CTRL+G').save(path)
            self.assertEqual(Settings.load(path).start_hotkey, 'CTRL+G')
            path.write_text('{"rod_key": "4"}')
            config = Settings.load(path)
            self.assertEqual(config.start_hotkey, 'INSERT')
            self.assertEqual(config.rod_key, '4')
