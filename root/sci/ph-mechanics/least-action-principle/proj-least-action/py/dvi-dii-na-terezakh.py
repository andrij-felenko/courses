def parabola(t):                       # справжній шлях
    return 0.5*g*T*t - 0.5*g*t**2

N  = 100
dt = T / N
t  = np.linspace(0, T, N + 1)
apex = g*T**2 / 8                       # 4.9 м

x_true = parabola(t)
x_fake = np.where(t <= T/2, apex*(t/(T/2)),      # трикутник:
                            apex*((T - t)/(T/2))) # два прямі відрізки

print(action(x_true[1:-1], dt))        # -> -32.01
print(action(x_fake[1:-1], dt))        # -> -24.01
