def analytic_signal(x):
    """x + j·H{x}: обнуляємо від'ємні частоти, подвоюємо додатні."""
    N = len(x)
    X = np.fft.fft(x)
    h = np.zeros(N)
    h[0] = 1                    # стала складова — лишаємо як є
    if N % 2 == 0:
        h[N//2]    = 1          # частота Найквіста — як є
        h[1:N//2]  = 2          # решта додатних — подвоїти
    else:
        h[1:(N+1)//2] = 2
    return np.fft.ifft(X * h)

env_hil = np.abs(analytic_signal(x))    # миттєва амплітуда = обвідна
