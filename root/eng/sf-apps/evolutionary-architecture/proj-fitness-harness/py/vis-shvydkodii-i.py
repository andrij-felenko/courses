@dataclass(frozen=True)
class Reading:                            # обидві величини з ОДНОГО артефакту
    p95_ms: float
    artifact_kb: int

@dataclass(frozen=True)
class Budget:
    max_p95_ms: float
    max_artifact_kb: int

def budget(measure: Callable[[], Reading], b: Budget) -> FitnessFunction:
    def run() -> Verdict:
        r = measure()                     # один прогін — обидві величини разом
        over = []
        if r.p95_ms > b.max_p95_ms:
            over.append(f"p95 {r.p95_ms:.0f}мс > {b.max_p95_ms:.0f}мс")
        if r.artifact_kb > b.max_artifact_kb:
            over.append(f"артефакт {r.artifact_kb}КБ > {b.max_artifact_kb}КБ")
        detail = "; ".join(over) if over else "обидва бюджети витримано"
        return Verdict(not over, detail)  # тримаються ОБИДВА — чи жодного розміну
    return FitnessFunction("budget", "швидкодія + постачання: час і розмір разом", run)
