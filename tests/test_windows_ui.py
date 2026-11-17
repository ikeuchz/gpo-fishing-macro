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
        finally:
            root.destroy()
