import tempfile
from pathlib import Path
import threading
import unittest
import numpy as np
from gpo_macro.config import Settings
from gpo_macro.vision import mask, detect, Controller
from gpo_macro.engine import Engine


class FakeInput:
    def __init__(self):
        self.held = False
        self.keys = []
        self.focus = True
    def focused(self, title): return self.focus
    def hold(self, value): self.held = value
    def key(self, value): self.keys.append(value)


class MacroTests(unittest.TestCase):
    def test_color_difference_does_not_wrap(self):
        image = np.array([[[0, 0, 0, 255]]], dtype=np.uint8)
        self.assertFalse(mask(image, (255, 255, 255), 4)[0, 0])
        self.assertTrue(mask(image, (2, 2, 2), 4)[0, 0])

    def test_detect_vertical_bar_and_gap(self):
        image = np.zeros((100, 30, 4), dtype=np.uint8)
        image[5:95, 5:25, :3] = (25, 25, 25)
        image[10:90, 7:23, :3] = (255, 170, 85)
        image[40:60, 7:23, :3] = (25, 25, 25)
        image[65:70, 12:18, :3] = 255
        target = detect(image, Settings())
        self.assertIsNotNone(target)
        self.assertEqual(target.white_y, 67)
        self.assertEqual(target.gap_y, 49.5)
        self.assertEqual(target.white_height, 5)
        self.assertGreater(target.error, 0)

    def test_missing_target_is_none(self):
        self.assertIsNone(detect(np.zeros((40, 40, 4), dtype=np.uint8), Settings()))

    def test_controller_direction_and_reset(self):
        controller = Controller(.05, 1)
        self.assertTrue(controller.hold(-1))
        self.assertFalse(controller.hold(1))
        controller.reset()
        self.assertTrue(controller.hold(-.1))

    def test_settings_roundtrip_and_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'settings.json'
            Settings().save(path)
            self.assertEqual(Settings.load(path), Settings())
        for value in (float('nan'), float('inf'), -1):
            with self.assertRaises(ValueError): Settings(kp=value).validate()
        with self.assertRaises(ValueError): Settings(auto_buy=True).validate()
        with self.assertRaises(ValueError): Settings(rod_key='ctrl+a').validate()

    def test_stop_releases_mouse_before_cast(self):
        inputs = FakeInput()
        inputs.hold(True)
        stop = threading.Event()
        stop.set()
        Engine(Settings(), inputs, stop, lambda text: None).run(lambda: None)
        self.assertFalse(inputs.held)
        self.assertEqual(inputs.keys, [])

    def test_focus_loss_releases_mouse(self):
        inputs = FakeInput()
        inputs.hold(True)
        inputs.focus = False
        Engine(Settings(), inputs, threading.Event(), lambda text: None).run(lambda: None)
        self.assertFalse(inputs.held)
        self.assertEqual(inputs.keys, [])

    def test_no_bite_recasts_and_can_stop(self):
        inputs = FakeInput()
        stop = threading.Event()
        now = [0.0]
        engine = Engine(Settings(auto_cast=True, bite_timeout=.05, interval=.01), inputs, stop,
                        lambda text: None, clock=lambda: now[0])
        casts = []
        def cast():
            casts.append(now[0])
            if len(casts) == 2:
                stop.set()
        engine.cast = cast
        def capture():
            now[0] += .02
            return np.zeros((40, 40, 4), dtype=np.uint8)
        def wait(seconds):
            engine.guard()
            now[0] += seconds
        engine.wait = wait
        engine.run(capture)
        self.assertEqual(len(casts), 2)
        self.assertEqual(engine.cycles, 0)
        self.assertFalse(inputs.held)

    def test_capture_error_releases_mouse(self):
        inputs = FakeInput()
        inputs.hold(True)
        engine = Engine(Settings(), inputs, threading.Event(), lambda text: None)
        def cast(): inputs.hold(True)
        engine.cast = cast
        def broken(): raise RuntimeError('capture failed')
        with self.assertRaises(RuntimeError): engine.run(broken)
        self.assertFalse(inputs.held)


if __name__ == '__main__':
    unittest.main()
