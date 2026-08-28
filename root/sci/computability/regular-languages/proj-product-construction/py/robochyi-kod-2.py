def ends_with(pattern, alphabet):
    """«Слово закінчується на pattern».
    Стан i = довжина найдовшого суфікса прочитаного, що є префіксом pattern."""
    m = len(pattern)
    delta = {}
    for i in range(m + 1):
        for c in alphabet:
            cand = pattern[:i] + c          # що тепер у хвості
            k = 0
            for k2 in range(min(len(cand), m), 0, -1):
                if cand.endswith(pattern[:k2]):
                    k = k2                  # найдовший префікс, що лишився суфіксом
                    break
            delta[(i, c)] = k
    return DFA(alphabet, set(range(m + 1)), delta, 0, {m})

def contains(pattern, alphabet):
    """«Слово МІСТИТЬ pattern». Той самий кістяк — стан m стає пасткою."""
    a = ends_with(pattern, alphabet)
    m = len(pattern)
    delta = dict(a.delta)
    for c in alphabet:
        delta[(m, c)] = m                   # ← уся різниця
    return DFA(alphabet, a.states, delta, 0, {m})

def not_starting_with(bad, alphabet):
    """«Слово непорожнє й НЕ починається з bad»."""
    delta = {}
    for c in alphabet:
        delta[("поч", c)] = "мертв" if c == bad else "ок"
        delta[("ок", c)] = "ок"
        delta[("мертв", c)] = "мертв"
    return DFA(alphabet, {"поч", "ок", "мертв"}, delta, "поч", {"ок"})
