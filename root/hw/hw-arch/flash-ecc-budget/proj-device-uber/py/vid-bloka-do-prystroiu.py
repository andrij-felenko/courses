@lru_cache(maxsize=None)
def block_uber(code: Code, pe_cycles: int) -> float:
    """UBER блока = частота відмов слова, поділена на довжину слова (JESD218)."""
    return word_failure_prob(code, rber(pe_cycles)) / code.n


def device_uber(code: Code, wear: list[int]) -> float:
    """UBER пристрою = середнє по блоках (читання розкладені рівномірно)."""
    return fsum(block_uber(code, e) for e in wear) / len(wear)


def risk_profile(code: Code, wear: list[int]) -> list[float]:
    """Внесок кожного блока в UBER пристрою, від найбільшого."""
    return sorted((block_uber(code, e) / len(wear) for e in wear), reverse=True)
