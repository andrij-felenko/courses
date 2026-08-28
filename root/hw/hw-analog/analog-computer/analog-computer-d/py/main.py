from math import sqrt

# Власна частота пружинного маятника, що його моделює машина.
# k — жорсткість (Н/м), m — маса (кг); повертає рад/с.
def spring_omega(k, m):
    return sqrt(k / m)            # ω = √(k/m)

# Масштаб блоку зворотного зв'язку k/m задаємо відношенням резисторів R_fb/R_in.
def feedback_gain(k, m):
    return k / m                  # напр. 8/2 = 4  → R_fb : R_in = 4 : 1

# spring_omega(8, 2) -> 2.0 рад/с;  feedback_gain(8, 2) -> 4.0
