"""Click-through visual guides, drawn outside the captured rectangle."""
import tkinter as tk


class TrackingOverlay:
    PAD = 65

    def __init__(self, root, inputs, area):
        self.area = area
        self.window = tk.Toplevel(root, takefocus=False)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', 'black')
        x, y, width, height = area
        self.window.geometry(f'{width+2*self.PAD}x{height+16}{x-self.PAD:+d}{y-8:+d}')
        self.canvas = tk.Canvas(self.window, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.create_rectangle(self.PAD-2, 6, self.PAD+width+2, height+10,
                                     outline='#51e086', width=2)
        self.window.update_idletasks()
        inputs.make_clickthrough(self.window)
        self.window.deiconify()
        self.window.update_idletasks()
        inputs.place_overlay(self.window, x-self.PAD, y-8, width+2*self.PAD, height+16)

    def update(self, target):
        self.canvas.delete('marker')
        if target is None:
            return
        p, width = self.PAD, self.area[2]
        fish, player = target.white_y+8, target.gap_y+8
        # Tips remain outside the ROI, so MSS never sees these indicators.
        self.canvas.create_polygon(p-7, fish, p-22, fish-7, p-22, fish+7,
                                   fill='white', tags='marker')
        self.canvas.create_text(p-38, fish-15, text='PEIXE', fill='white',
                                font=('Segoe UI', 7, 'bold'), tags='marker')
        self.canvas.create_polygon(p+width+7, player, p+width+22, player-7,
                                   p+width+22, player+7, fill='#45dbc2', tags='marker')
        self.canvas.create_text(p+width+34, player+16, text='VOCÊ', fill='#45dbc2',
                                font=('Segoe UI', 7, 'bold'), tags='marker')

    def close(self):
        self.window.destroy()
