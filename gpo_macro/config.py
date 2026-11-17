from dataclasses import asdict, dataclass, field
import json
import math
from .hotkeys import parse_shortcut
from pathlib import Path


@dataclass
class Settings:
    area: list[int] = field(default_factory=lambda: [970, 410, 190, 310])
    start_hotkey: str = 'INSERT'
    area_hotkey: str = 'HOME'
    exit_hotkey: str = 'END'
    rod_key: str = '1'
    other_key: str = '2'
    bite_timeout: float = 30.0
    end_timeout: float = 2.0
    cast_hold: float = 0.3
    interval: float = 0.02
    kp: float = 0.05
    kd: float = 1.0
    blue_tolerance: int = 8
    white_tolerance: int = 8
    gray_tolerance: int = 4
    foreground_title: str = 'Roblox'
    auto_buy: bool = False
    auto_store: bool = False
    auto_bait: bool = False
    buy_every: int = 20
    # Named points are absolute desktop pixels; routines use those names.
    points: dict = field(default_factory=dict)
    routines: dict = field(default_factory=lambda: {
        'bait': [{'click': 'bait'}, {'wait': 0.3}, {'click': 'water'}],
        'buy': [{'click': 'shop'}, {'wait': 0.5}, {'click': 'confirm'}],
        'store': [{'key': '3'}, {'wait': 0.5}, {'click': 'store'}],
    })

    def validate(self):
        shortcuts = [parse_shortcut(value) for value in
                     (self.start_hotkey, self.area_hotkey, self.exit_hotkey)]
        if len(set(shortcuts)) != 3:
            raise ValueError('Escolha três atalhos diferentes para iniciar, área e sair.')
        if not isinstance(self.points, dict) or not isinstance(self.routines, dict):
            raise ValueError('points e routines devem ser objetos JSON.')
        if any(type(v) is not bool for v in (self.auto_buy, self.auto_store, self.auto_bait)):
            raise ValueError('As opções de automação devem ser true ou false.')
        if len(self.area) != 4 or any(type(v) is not int for v in self.area):
            raise ValueError('Área deve conter quatro inteiros: x, y, largura, altura.')
        if not (10 <= self.area[2] <= 10000 and 10 <= self.area[3] <= 10000):
            raise ValueError('Largura e altura devem estar entre 10 e 10000.')
        for name in ('bite_timeout', 'end_timeout', 'cast_hold', 'interval', 'kp', 'kd'):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f'{name}: use um número finito não negativo.')
        if self.bite_timeout == 0 or self.end_timeout == 0 or self.interval < .005:
            raise ValueError('Timeouts devem ser positivos; intervalo mínimo: 0.005 s.')
        for name in ('blue_tolerance', 'white_tolerance', 'gray_tolerance'):
            if not 0 <= getattr(self, name) <= 255:
                raise ValueError('Tolerância de cor deve estar entre 0 e 255.')
        if type(self.buy_every) is not int or self.buy_every < 1:
            raise ValueError('buy_every deve ser um inteiro positivo.')
        if not self.foreground_title.strip():
            raise ValueError('Informe parte do título da janela do jogo.')
        for key in (self.rod_key, self.other_key):
            self.validate_key(key)
        for point in self.points.values():
            if len(point) != 2 or any(type(v) is not int for v in point):
                raise ValueError('Cada ponto deve conter dois inteiros: x, y.')
        for name in ('bait', 'buy', 'store'):
            steps = self.routines.get(name)
            if not isinstance(steps, list) or len(steps) > 100:
                raise ValueError(f'Rotina {name}: use uma lista de até 100 ações.')
            for step in steps:
                if not isinstance(step, dict) or len(step) != 1:
                    raise ValueError('Cada ação deve ter apenas click, key ou wait.')
                action, value = next(iter(step.items()))
                if action == 'key':
                    self.validate_key(value)
                elif action == 'wait':
                    if not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 60:
                        raise ValueError('wait deve estar entre 0 e 60 segundos.')
                elif action == 'click':
                    if not isinstance(value, str):
                        raise ValueError('click deve indicar o nome de um ponto.')
                else:
                    raise ValueError(f'Ação desconhecida: {action}')
        for enabled, name in ((self.auto_bait, 'bait'), (self.auto_buy, 'buy'), (self.auto_store, 'store')):
            if enabled:
                if not self.routines[name]:
                    raise ValueError(f'Configure a rotina {name}.')
                for step in self.routines[name]:
                    if 'click' in step and step['click'] not in self.points:
                        raise ValueError(f'Capture o ponto: {step["click"]}')
        return self

    @staticmethod
    def validate_key(key):
        if not isinstance(key, str) or len(key) != 1 or key.upper() not in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            raise ValueError('Teclas dos itens e rotinas: use uma letra ou número.')

    @classmethod
    def load(cls, path):
        if not path.exists():
            return cls()
        return cls(**json.loads(path.read_text(encoding='utf-8'))).validate()

    def save(self, path):
        self.validate()
        temporary = Path(str(path) + '.tmp')
        temporary.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding='utf-8')
        temporary.replace(path)
