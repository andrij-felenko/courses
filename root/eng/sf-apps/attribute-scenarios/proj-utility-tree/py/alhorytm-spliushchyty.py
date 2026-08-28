from dataclasses import dataclass

@dataclass(frozen=True)
class Ranked:
    scenario: Scenario
    attribute: str
    score: int          # важливість × складність

def score(s: Scenario) -> int:
    return s.importance * s.difficulty   # ключова ухвала — ДОБУТОК, не сума

def rank(tree: UtilityTree) -> list[Ranked]:
    flat = [Ranked(s, attr.name, score(s))
            for attr in tree.attributes
            for s in attr.scenarios]
    # Спад за добутком; за рівних — важливіший, тоді складніший (детермінізм).
    flat.sort(key=lambda r: (r.score, r.scenario.importance, r.scenario.difficulty),
              reverse=True)
    return flat

def drivers(ranked: list[Ranked]) -> list[Ranked]:
    # Крайній квадрант (В, В): і найцінніше, і найважче.
    return [r for r in ranked
            if r.scenario.importance == 3 and r.scenario.difficulty == 3]
