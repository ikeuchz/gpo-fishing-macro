import threading
import unittest
import numpy as np
from gpo_macro.config import Settings
from gpo_macro.engine import Engine
from gpo_macro.vision import detect
from test_macro import FakeInput


def frame():
    image = np.zeros((110, 65, 4), dtype=np.uint8)
    image[5:100, 5:25, :3] = 25
    image[10:95, 7:23, :3] = (255,170,85)
    image[40:60, 7:23, :3] = 25
    image[65:70, 12:18, :3] = 255
    # Second (progress) bar: a different white position and a larger gap.
    image[5:100, 35:55, :3] = 25
    image[10:95, 37:53, :3] = (255,170,85)
    image[20:55, 37:53, :3] = 25
    image[80:85, 40:50, :3] = 255
    return image


class TrackingTests(unittest.TestCase):
    def test_separates_control_bar_from_progress(self):
        left = detect(frame(), Settings(control_bar='left'))
        right = detect(frame(), Settings(control_bar='right'))
        self.assertEqual(left.white_y, 67)
        self.assertEqual(left.gap_y, 49.5)
        self.assertEqual(right.white_y, 82)
        self.assertEqual(right.gap_y, 37)

    def test_no_target_if_white_only_in_progress(self):
        image = frame()
        image[65:70, 12:18, :3] = (255,170,85)
        self.assertIsNone(detect(image, Settings()))

    def test_no_cast_or_click_when_minigame_absent(self):
        inputs, stop = FakeInput(), threading.Event()
        actions = []
        inputs.hold = lambda value: actions.append(value)
        settings = Settings(bite_timeout=.01)
        ticks = [0]
        engine = Engine(settings, inputs, stop, lambda text: None, clock=lambda: ticks[0])
        def capture():
            ticks[0] += 100
            if ticks[0] >= 400:
                stop.set()
            return np.zeros((110,65,4), dtype=np.uint8)
        engine.wait = lambda seconds: engine.guard()
        engine.run(capture)
        self.assertEqual(inputs.keys, [])
        self.assertNotIn(True, actions)

    def test_single_frame_does_not_activate_input(self):
        inputs, stop = FakeInput(), threading.Event()
        actions = []
        inputs.hold = lambda value: actions.append(value)
        image = frame()
        # Put the fish above the player: tracking would require holding.
        image[65:70,12:18,:3] = (255,170,85)
        image[25:30,12:18,:3] = 255
        engine = Engine(Settings(), inputs, stop, lambda text: None)
        engine.wait = lambda seconds: stop.set()
        engine.run(lambda: image)
        self.assertNotIn(True, actions)

    def test_manual_mode_tracks_then_releases_without_recasting(self):
        inputs, stop = FakeInput(), threading.Event()
        actions, seen = [], []
        inputs.hold = lambda value: actions.append(value)
        image = frame()
        image[65:70,12:18,:3] = (255,170,85)
        image[25:30,12:18,:3] = 255
        ticks = [0]
        engine = Engine(Settings(end_timeout=.1), inputs, stop, lambda text: None,
                        clock=lambda: ticks[0]*.1, observe=seen.append)
        def capture():
            ticks[0] += 1
            if ticks[0] > 8:
                stop.set()
            return image if ticks[0] <= 4 else np.zeros_like(image)
        engine.wait = lambda seconds: engine.guard()
        engine.run(capture)
        self.assertIn(True, actions)
        self.assertFalse(actions[-1])
        self.assertEqual(inputs.keys, [])
        self.assertEqual(engine.cycles, 1)
        self.assertIsNone(seen[-1])
