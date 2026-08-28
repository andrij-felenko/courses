from dataclasses import dataclass

@dataclass
class Gap:
    who: str
    concern: Attr
    veto: bool
    score: int

def coverage_gaps(reg: list[Stakeholder], decisions: list[Decision]) -> list[Gap]:
    covered = {d.closes for d in decisions}                  # що архітектура вже закрила
    gaps = [Gap(s.name, s.concern, s.hard, salience_score(s))
            for s in reg if s.concern not in covered]         # турботи без відповіді
    gaps.sort(key=lambda g: (g.veto, g.score), reverse=True)  # тверді вето — вгору
    return gaps
