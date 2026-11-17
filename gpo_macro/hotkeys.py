"""Portable shortcut validation; Windows virtual-key values."""
NAMED = {'INSERT': 0x2D, 'HOME': 0x24, 'END': 0x23, 'PAGEUP': 0x21,
         'PAGEDOWN': 0x22, 'PAUSE': 0x13, 'SCROLLLOCK': 0x91,
         **{f'F{i}': 0x6F+i for i in range(1, 13)}}
MODIFIERS = {'CTRL': 0x11, 'ALT': 0x12, 'SHIFT': 0x10}


def parse_shortcut(text):
    if not isinstance(text, str):
        raise ValueError('Atalho deve ser um texto.')
    parts = [p.strip().upper() for p in text.split('+')]
    if not parts or any(not part for part in parts):
        raise ValueError('Informe um atalho, por exemplo INSERT ou CTRL+G.')
    modifiers, key = parts[:-1], parts[-1]
    if len(set(modifiers)) != len(modifiers) or any(p not in MODIFIERS for p in modifiers):
        raise ValueError('Use CTRL, ALT ou SHIFT antes da tecla.')
    if key in NAMED:
        code = NAMED[key]
    elif len(key) == 1 and key in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' and modifiers:
        code = ord(key)
    else:
        raise ValueError('Use INSERT, HOME, END, PAGEUP, PAGEDOWN, PAUSE, F1–F12 ou uma letra/número com modificador.')
    return code, frozenset(MODIFIERS[p] for p in modifiers)


def active_shortcuts(bindings, is_down):
    # Exact modifiers prevent HOME and CTRL+HOME from firing together.
    modifiers = frozenset(code for code in MODIFIERS.values() if is_down(code))
    return {name for name, text in bindings.items()
            if (parsed := parse_shortcut(text))[1] == modifiers and is_down(parsed[0])}
