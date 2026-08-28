def rank_by_roi(strategies: list[Strategy]) -> list[Strategy]:
    # Перший зріз: за ROI спадно. O(n log n).
    return sorted(strategies, key=lambda s: s.roi(), reverse=True)

def greedy_pick(strategies: list[Strategy], budget: float):
    # Іди по ранжованому списку й бери все, що ще влазить у бюджет.
    chosen, spent = [], 0.0
    for s in rank_by_roi(strategies):
        if spent + s.cost <= budget:
            chosen.append(s)
            spent += s.cost
    total = sum(s.benefit() for s in chosen)
    return chosen, spent, total
