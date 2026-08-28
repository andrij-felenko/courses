def rainflow(reversals):
    """Чотириточковий rainflow. Повертає (замкнені_цикли, залишок).
    Кожен замкнений цикл — (амплітуда, середнє). Залишок — те, що не замкнулось."""
    stack = []
    cycles = []
    for p in reversals:
        stack.append(p)
        while len(stack) >= 4:
            a, b, c, d = stack[-4], stack[-3], stack[-2], stack[-1]
            inner   = abs(c - b)      # внутрішній розмах (між середніми точками)
            left    = abs(b - a)      # розмах ліворуч
            right   = abs(d - c)      # розмах праворуч
            if inner <= left and inner <= right:
                amp  = inner / 2.0
                mean = (b + c) / 2.0
                cycles.append((amp, mean))
                del stack[-3:-1]      # вийняти дві внутрішні точки (b, c)
                # крайні a і d зімкнулись — петля крутиться далі
            else:
                break                 # цикл ще не дозрів, чекаємо наступний реверс
    return cycles, stack              # у стеку лишився ЗАЛИШОК (residue)
