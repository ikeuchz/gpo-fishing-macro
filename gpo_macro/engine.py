import time
from .vision import Controller, detect


class Interrupted(Exception):
    pass


class Engine:
    def __init__(self, settings, inputs, stop, notify, clock=time.monotonic, observe=None):
        self.settings, self.inputs, self.stop = settings, inputs, stop
        self.notify, self.clock = notify, clock
        self.controller = Controller(settings.kp, settings.kd)
        self.cycles = 0
        self.observe = observe or (lambda target: None)

    def guard(self):
        if self.stop.is_set():
            raise Interrupted('Parado')
        if not self.inputs.focused(self.settings.foreground_title):
            raise Interrupted('Parado: a janela do jogo perdeu o foco')

    def wait(self, seconds):
        deadline = self.clock() + seconds
        while True:
            self.guard()
            remaining = deadline - self.clock()
            if remaining <= 0:
                return
            self.stop.wait(min(.02, remaining))

    def click(self, point=None, duration=.05):
        self.guard()
        if point is not None:
            self.inputs.move(point)
        try:
            self.inputs.hold(True)
            self.wait(duration)
        finally:
            self.inputs.hold(False)

    def key(self, value):
        self.guard()
        self.inputs.key(value)

    def routine(self, name):
        self.notify(f'Rotina: {name}')
        for step in self.settings.routines[name]:
            self.guard()
            if 'click' in step:
                self.click(self.settings.points[step['click']])
                self.wait(.15)
            elif 'key' in step:
                self.key(step['key'])
            else:
                self.wait(step['wait'])

    def cast(self):
        self.controller.reset()
        self.key(self.settings.other_key)
        self.wait(.3)
        self.key(self.settings.rod_key)
        self.wait(.3)
        if self.settings.auto_bait:
            self.routine('bait')
        self.click(duration=self.settings.cast_hold)
        self.notify('Aguardando fisgada')

    def run(self, capture):
        try:
            self.settings.validate()
            self.guard()
            if self.settings.auto_cast:
                if self.settings.auto_buy:
                    self.routine('buy')
                self.cast()
            else:
                self.notify('Aguardando minigame: lance a vara manualmente')
            cast_at = self.clock()
            last_seen = None
            confirmed = False
            stable = 0
            while True:
                self.guard()
                target = detect(capture(), self.settings)
                now = self.clock()
                self.observe(target)
                if target is not None:
                    stable += 1
                    if not confirmed and stable >= 3:
                        confirmed = True
                        self.notify('Acompanhando peixe branco — barra de controle')
                    if confirmed:
                        last_seen = now
                        self.guard()
                        self.inputs.hold(self.controller.hold(target.error))
                else:
                    stable = 0
                    self.inputs.hold(False)
                    self.controller.reset()
                    if confirmed and last_seen is not None and now - last_seen >= self.settings.end_timeout:
                        self.cycles += 1
                        self.notify(f'Ciclos encerrados: {self.cycles}')
                        if self.settings.auto_store:
                            self.routine('store')
                        if self.settings.auto_cast:
                            if self.settings.auto_buy and self.cycles % self.settings.buy_every == 0:
                                self.routine('buy')
                            self.cast()
                        else:
                            self.notify('Minigame encerrado. Aguardando o próximo, sem puxar a vara.')
                        cast_at, last_seen, confirmed = self.clock(), None, False
                    elif self.settings.auto_cast and not confirmed and now - cast_at >= self.settings.bite_timeout:
                        self.notify('Sem fisgada: relançando (lançamento automático ativado)')
                        self.cast()
                        cast_at = self.clock()
                self.wait(self.settings.interval)
        except Interrupted as error:
            self.notify(str(error))
        finally:
            self.observe(None)
            self.inputs.hold(False)
