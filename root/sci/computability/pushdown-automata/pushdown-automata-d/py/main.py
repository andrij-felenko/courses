PAIRS = {')': '(', ']': '[', '}': '{'}   # закривна → її відкривна пара

def balanced(s):
    stack = []                        # магазин; порожній стек — це «на дні лише Z₀»
    for c in s:
        if c in '([{':                # відкривна: кладемо на вершину (push)
            stack.append(c)
        elif c in ')]}':              # закривна: знімаємо вершину (pop)
            if not stack:             # нíчого знімати → закривних забагато
                return False
            if stack.pop() != PAIRS[c]:   # вершина не пасує до цієї дужки
                return False
    return not stack                  # прийом ⟺ стек порожній
