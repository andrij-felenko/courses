def rising_zeros(s, hyst=0.25):
    """Моменти (у відліках, дробові), коли сигнал іде знизу вгору через своє середнє.
    Гістерезис: перехід зараховуємо лише після провалу нижче −thr."""
    s = s - s.mean()
    thr = hyst * math.sqrt(2.0) * s.std()          # частка амплітуди: A ≈ √2·σ
    out, armed = [], False
    for i in range(1, len(s)):
        if s[i] < -thr:
            armed = True
        elif armed and s[i - 1] <= 0.0 < s[i]:
            out.append(i - 1 + (-s[i - 1]) / (s[i] - s[i - 1]))    # уточнення моменту
            armed = False
    return out


def channel_freq(s, fs, hyst=0.25):
    """Частота каналу: цілі періоди між ПЕРШИМ і ОСТАННІМ перетином."""
    z = rising_zeros(s, hyst)
    if len(z) < 2:
        return 0.0
    return (len(z) - 1) * fs / (z[-1] - z[0])


def freq_ratio(x, y, fs, max_den=16, tol=1e-3):
    """Відношення частот двох каналів як нескоротний дріб p : q."""
    fx, fy = channel_freq(x, fs), channel_freq(y, fs)
    p, q = rationalize(fx / fy, max_den)
    if abs(fx / fy - p / q) / (fx / fy) > tol:
        raise ValueError("частоти не в простому відношенні")
    return p, q, fx, fy
