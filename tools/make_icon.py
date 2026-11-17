"""Draw the project's original fish icon. Requires Pillow for asset creation only."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / 'gpo_macro' / 'assets'
root.mkdir(parents=True, exist_ok=True)
image = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(image)
d.rounded_rectangle((4, 4, 252, 252), radius=56, fill='#141f32')
d.arc((37, 36, 217, 216), 190, 340, fill='#45dbc2', width=9)
d.line([(175, 38), (175, 100)], fill='#e5edf9', width=8)
d.arc((146, 84, 178, 126), 0, 180, fill='#e5edf9', width=8)
d.polygon([(58, 146), (30, 120), (30, 175)], fill='#45dbc2')
d.ellipse((51, 109, 202, 181), fill='#45dbc2')
d.polygon([(100, 115), (135, 92), (151, 118)], fill='#45dbc2')
d.ellipse((170, 132, 181, 143), fill='#0b1220')
d.arc((42, 166, 218, 220), 8, 172, fill='#9eafc7', width=6)
image.save(root/'app.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
image.resize((64,64), Image.Resampling.LANCZOS).save(root/'app.png')
