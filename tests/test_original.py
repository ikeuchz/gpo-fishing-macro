import hashlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import numpy as np

# On Linux only, stub Windows-only imports; do not create hooks or send inputs.
if sys.platform != 'win32':
    for name in ('keyboard', 'mss', 'win32api', 'win32con', 'win32gui'):
        sys.modules[name] = types.ModuleType(name)
    pynput = types.ModuleType('pynput')
    pynput.mouse = types.ModuleType('pynput.mouse')
    sys.modules['pynput'] = pynput
    sys.modules['pynput.mouse'] = pynput.mouse
    sys.modules['win32con'].MOUSEEVENTF_MOVE = 1
    sys.modules['win32con'].MOUSEEVENTF_LEFTDOWN = 2
    sys.modules['win32con'].MOUSEEVENTF_LEFTUP = 4

from gpo_macro.original import OriginalMacro, CORE_SHA256, core
from gpo_macro.app import App
from gpo_macro.hotkeys import parse_shortcut


class OriginalCoreTests(unittest.TestCase):
    def test_core_resource_is_exact_original_archive_entry(self):
        path = Path(__file__).resolve().parents[1]/'gpo_macro/assets/original_core.marshal'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), CORE_SHA256)

    def test_fishing_methods_are_inherited_without_reimplementation(self):
        methods = ('main_loop', 'find_color_positions', 'cast_rod', 'perform_auto_buy',
                   'perform_store_fruit', 'save_settings', 'save_timeouts', 'save_pd_gains',
                   'save_color_tolerances', 'capture_point', 'change_area', 'on_area_selected',
                   'show_scan_outline', 'hide_scan_outline', 'get_arrow_coords_horizontal_left',
                   'update_or_create_arrow', 'toggle_start_stop', 'save_auto_buy_settings',
                   'save_auto_store_settings', 'save_auto_select_bait_settings',
                   'toggle_auto_buy', 'toggle_auto_store', 'toggle_auto_select_bait')
        for name in methods:
            with self.subTest(method=name):
                self.assertIs(getattr(App, name), getattr(OriginalMacro, name))

    def test_original_color_search(self):
        rig = object.__new__(OriginalMacro)
        image = np.zeros((20, 30, 4), dtype=np.uint8)
        image[3:12, 5:15, :3] = (255, 170, 85)
        self.assertEqual(rig.find_color_positions(image, (85,170,255), 0), ((5,3), (14,3)))
        self.assertEqual(rig.find_color_positions(image, (255,255,255), 0), (None,None))

    def test_cast_uses_original_keys_and_mouse_sequence(self):
        rig = types.SimpleNamespace(not_rod_key='2', rod_key='1', auto_select_bait=False)
        events = []
        keyboard = types.SimpleNamespace(press=lambda key: events.append(('down',key)),
                                         release=lambda key: events.append(('up',key)))
        api = types.SimpleNamespace(mouse_event=lambda flag,*args: events.append(('mouse',flag)))
        with patch.object(core, 'keyboard', keyboard), patch.object(core, 'win32api', api), \
             patch.object(core.time, 'sleep', lambda seconds: None):
            OriginalMacro.cast_rod(rig)
        self.assertEqual(events[:4], [('down','2'),('up','2'),('down','1'),('up','1')])
        flags = [event[1] for event in events if event[0]=='mouse']
        self.assertIn(core.win32con.MOUSEEVENTF_LEFTDOWN, flags)
        self.assertEqual(flags[-1], core.win32con.MOUSEEVENTF_LEFTUP)

    def test_old_launcher_is_not_invoked(self):
        self.assertEqual(core.__name__, '_gpo_original')
        self.assertTrue(callable(core.auto_subscribe_to_youtube))
        self.assertTrue(callable(core.main))

    def test_custom_shortcuts(self):
        self.assertEqual(parse_shortcut('CTRL+G'), (ord('G'), frozenset({0x11})))
        self.assertEqual(parse_shortcut('INSERT')[0], 0x2D)
        with self.assertRaises(ValueError): parse_shortcut('CTRL+')


@unittest.skipUnless(sys.platform == 'win32', 'Windows UI integration')
class WindowsUITests(unittest.TestCase):
    def test_original_settings_widgets_and_new_presentation(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        app = None
        try:
            # Exercise real original construction; register no global hooks in CI.
            with patch.object(App, 'setup_hotkeys', lambda self: None):
                app = App(root)
            root.update_idletasks()
            self.assertFalse(app.is_running)
            self.assertEqual(app.keybindings['start_stop'], 'INSERT')
            for field in ('kp_entry', 'kd_entry', 'bite_timeout_entry', 'end_fish_timeout_entry',
                          'blue_tolerance_entry', 'white_tolerance_entry', 'gray_tolerance_entry'):
                self.assertTrue(getattr(app, field).winfo_exists())
            app.toggle_compact()
            self.assertTrue(app.compact_mode)
            app.toggle_compact()
            self.assertFalse(app.compact_mode)
            app.start_delayed()
            self.assertIsNotNone(app.pending_start)
            app.stop_button()
            self.assertIsNone(app.pending_start)
            self.assertFalse(app.is_running)
        finally:
            root.destroy()
