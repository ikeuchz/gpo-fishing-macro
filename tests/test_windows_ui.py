import sys
import unittest


@unittest.skipUnless(sys.platform == 'win32', 'Windows GUI integration')
class WindowsUITests(unittest.TestCase):
    def test_window_and_settings_form(self):
        import tkinter as tk
        from gpo_macro.app import App
        root = tk.Tk()
        root.withdraw()
        try:
            app = App(root)
            root.update_idletasks()
            settings = app.read_settings()
            self.assertGreater(settings.area[2], 0)
            self.assertEqual(settings.rod_key, '1')
            self.assertEqual(len(app.inputs.position()), 2)
            self.assertFalse(app.busy())
            self.assertTrue(root.attributes('-topmost'))
            app.show_overlay([100, 100, 100, 240])
            from gpo_macro.vision import Target
            app.overlay.update(Target(70, 95, 5))
            self.assertEqual(len(app.overlay.canvas.find_withtag('marker')), 4)
            app.overlay.update(None)
            self.assertEqual(len(app.overlay.canvas.find_withtag('marker')), 0)
            app.toggle_compact()
            self.assertTrue(app.compact_mode)
            app.toggle_compact()
            self.assertFalse(app.compact_mode)
            self.assertEqual(app.fields['start_hotkey'].get(), 'INSERT')
            from unittest.mock import Mock
            app.save = Mock(return_value=True)
            app.start_from_button()
            self.assertIsNotNone(app.start_pending)
            app.stop_from_button()
            self.assertIsNone(app.start_pending)
            self.assertTrue(app.stop.is_set())
            app.toggle = Mock()
            app.countdown(0)
            app.toggle.assert_called_once()
        finally:
            root.destroy()
