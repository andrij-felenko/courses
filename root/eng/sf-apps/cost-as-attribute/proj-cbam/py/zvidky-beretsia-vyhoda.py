from dataclasses import dataclass

# Внесок стратегії в ОДИН атрибут: вага стейкхолдера й корисність до/після (0..100).
@dataclass
class Contribution:
    attribute: str
    weight: float        # наскільки атрибут важливий стейкхолдерам
    before: float        # корисність зараз
    after: float         # корисність, якщо стратегію впровадити

@dataclass
class Strategy:
    name: str
    cost: float                    # вартість, тижні
    contribs: list[Contribution]

    def benefit(self) -> float:
        # CBAM: вигода = Σ вага·(корисність_після − корисність_до)
        return sum(c.weight * (c.after - c.before) for c in self.contribs)

    def roi(self) -> float:
        return self.benefit() / self.cost if self.cost else float("inf")
