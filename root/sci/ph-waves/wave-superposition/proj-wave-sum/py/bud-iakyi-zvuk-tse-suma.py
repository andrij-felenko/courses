import numpy as np

fs = 44_100
t  = np.arange(int(fs * 1.0)) / fs
f0 = 220.0

def square_from_sines(n_harm):
    y = np.zeros_like(t)
    for k in range(1, 2*n_harm, 2):        # тільки непарні: 1, 3, 5, …
        y += np.sin(2*np.pi*k*f0*t) / k    # амплітуда k-ї гармоніки = 1/k
    return (4/np.pi) * y

approx = square_from_sines(8)    # усього 8 непарних гармонік — уже впізнаваний квадрат
