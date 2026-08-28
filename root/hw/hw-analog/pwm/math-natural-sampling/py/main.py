import math

def natural_edge(y: float, M: float, q: float) -> float:
    """Фаза краю x_e для природної вибірки: розв'язок x = πM·cos(y − (x+π)/q).

    y — фаза сигналу на початку періоду несучої; M — глибина модуляції; q = f_c/f0.
    Відображення стискне (|похідна| ≤ πM/q ≪ 1), тож вистачає трьох ітерацій.
    """
    x = math.pi * M * math.cos(y)             # старт = те, що дала б рівномірна вибірка
    for _ in range(3):
        x = math.pi * M * math.cos(y - (x + math.pi) / q)
    return x
