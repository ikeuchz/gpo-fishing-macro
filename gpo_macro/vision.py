from dataclasses import dataclass
import numpy as np


def mask(image, rgb, tolerance):
    # MSS supplies BGRA; signed conversion avoids uint8 subtraction wrapping.
    bgr = image[..., :3].astype(np.int16)
    return np.all(np.abs(bgr - np.array(rgb[::-1], dtype=np.int16)) <= tolerance, axis=2)


@dataclass(frozen=True)
class Target:
    white_y: float
    gap_y: float
    white_height: int

    @property
    def error(self):
        return (self.white_y - self.gap_y) / max(2 * self.white_height, 1)


def detect(image, settings):
    blue = mask(image, (85, 170, 255), settings.blue_tolerance)
    ys, xs = np.where(blue)
    if len(xs) < 4:
        return None
    left, right = int(xs.min()), int(xs.max()) + 1
    crop = image[:, left:right]
    gray_rows = np.flatnonzero(mask(crop, (25, 25, 25), settings.gray_tolerance).any(axis=1))
    if len(gray_rows) < 2:
        return None
    top, bottom = int(gray_rows.min()), int(gray_rows.max()) + 1
    crop = crop[top:bottom]
    white_rows = np.flatnonzero(mask(crop, (255, 255, 255), settings.white_tolerance).any(axis=1))
    if not len(white_rows):
        return None
    gap_rows = np.flatnonzero(~mask(crop, (85, 170, 255), settings.blue_tolerance).any(axis=1))
    if not len(gap_rows):
        return None
    sections = np.split(gap_rows, np.flatnonzero(np.diff(gap_rows) != 1) + 1)
    gap = max(sections, key=len)
    return Target(float((white_rows[0] + white_rows[-1]) / 2 + top),
                  float((gap[0] + gap[-1]) / 2 + top),
                  int(white_rows[-1] - white_rows[0] + 1))


class Controller:
    def __init__(self, kp, kd):
        self.kp, self.kd = kp, kd
        self.previous = None

    def hold(self, error):
        derivative = 0 if self.previous is None else error - self.previous
        self.previous = error
        return self.kp * error + self.kd * derivative < 0

    def reset(self):
        self.previous = None
