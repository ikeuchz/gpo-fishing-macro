from dataclasses import dataclass
import numpy as np


def mask(image, rgb, tolerance):
    bgr = image[..., :3].astype(np.int16)
    return np.all(np.abs(bgr - np.array(rgb[::-1], dtype=np.int16)) <= tolerance, axis=2)


def runs(indices):
    return np.split(indices, np.flatnonzero(np.diff(indices) != 1) + 1) if len(indices) else []


@dataclass(frozen=True)
class Target:
    white_y: float
    gap_y: float
    white_height: int

    @property
    def error(self):
        return (self.white_y - self.gap_y) / max(2 * self.white_height, 1)


def detect(image, settings):
    """Read only one blue vertical bar; never combine it with the progress bar."""
    blue = mask(image, (85, 170, 255), settings.blue_tolerance)
    columns = np.flatnonzero(blue.sum(axis=0) >= 3)
    bars = [r for r in runs(columns) if len(r) >= 4]
    if not bars:
        return None
    bar = bars[0] if settings.control_bar == 'left' else bars[-1]
    left, right = int(bar[0]), int(bar[-1]) + 1
    blue_rows = np.flatnonzero(blue[:, left:right].any(axis=1))
    if len(blue_rows) < 10:
        return None
    # Exclude gray margins above/below the actual blue track.
    top, bottom = int(blue_rows[0]), int(blue_rows[-1]) + 1
    crop = image[top:bottom, left:right]
    if not mask(crop, (25, 25, 25), settings.gray_tolerance).any():
        return None
    white_rows = np.flatnonzero(mask(crop, (255, 255, 255), settings.white_tolerance).any(axis=1))
    whites = runs(white_rows)
    gaps = runs(np.flatnonzero(~blue[top:bottom, left:right].any(axis=1)))
    # A player's gap must be inside the track, not a blank outer margin.
    gaps = [r for r in gaps if r[0] > 0 and r[-1] < bottom-top-1]
    if not whites or not gaps:
        return None
    fish = max(whites, key=len)
    gap = max(gaps, key=len)
    return Target(float((fish[0] + fish[-1]) / 2 + top),
                  float((gap[0] + gap[-1]) / 2 + top), int(len(fish)))


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
