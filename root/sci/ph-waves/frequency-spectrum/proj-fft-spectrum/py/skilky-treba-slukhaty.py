def peak_freq(f, a):
    k = int(np.argmax(a))                                    # найвищий бін
    d = 0.5*(a[k-1] - a[k+1]) / (a[k-1] - 2*a[k] + a[k+1])   # вершина параболи
    return (k + d) * (f[1] - f[0])                           # (k + зсув)·Δf

fs, N = 1000, 1000
t = np.arange(N) / fs
for ftone in (100.37, 137.83):
    f, a = spectrum(np.sin(2*np.pi*ftone*t), fs, np.hanning)
    print("справжня %.2f Гц -> бін %.0f Гц -> уточнено %.3f Гц"
          % (ftone, f[int(np.argmax(a))], peak_freq(f, a)))
