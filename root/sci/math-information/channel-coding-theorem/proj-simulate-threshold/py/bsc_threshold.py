# bsc_threshold.py — поріг Шеннона на власні очі
import numpy as np
from math import comb

_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)

def popcount(a):
    """Кількість одиничних бітів — побайтово через таблицю (numpy < 2.0 не має bitwise_count)."""
    a = np.asarray(a, dtype=np.uint32)
    return (_POP[a & 0xFF].astype(np.int64) + _POP[(a >> 8) & 0xFF]
            + _POP[(a >> 16) & 0xFF] + _POP[(a >> 24) & 0xFF])

def h2(p):
    """Двійкова ентропія, біт."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)

def capacity(p):
    return 1.0 - h2(p)

def random_codebook(k, n, rng):
    """M = 2^k слів довжини n, кинутих навмання — саме той ансамбль, про який теорема."""
    return rng.integers(0, 2, size=(1 << k, n), dtype=np.int8)

def repetition_codebook(r):
    """Повторний код як книга з двох слів: 000… і 111…"""
    return np.array([[0] * r, [1] * r], dtype=np.int8)

def simulate(book, p, trials, rng, chunk=64):
    """Ганяє книгу крізь BSC. Декодер — найближчий сусід (він же ML).
    Повертає: (кількість блокових похибок, частка блокових, частка бітових)."""
    M, n = book.shape
    k = int(round(np.log2(M)))
    pm = 2 * book.astype(np.float32) - 1          # книга у ±1, рахуємо один раз
    blk = 0
    bit = 0
    for s in range(0, trials, chunk):             # пачками — інакше t×M не влізе в пам'ять
        t = min(chunk, trials - s)
        msg = rng.integers(0, M, size=t)
        noise = (rng.random((t, n)) < p).astype(np.int8)
        recv = book[msg] ^ noise                  # канал: незалежний переворот кожного біта
        corr = (2 * recv.astype(np.float32) - 1) @ pm.T    # t×M скалярних добутків
        guess = np.argmax(corr, axis=1)           # max добуток = min відстань
        blk += int((guess != msg).sum())
        bit += int(popcount(guess ^ msg).sum())   # біти повідомлення = двійковий запис індексу
    return blk, blk / trials, bit / (trials * k)

def rep_ber(r, p):
    """Точна залишкова похибка мажоритарного повторення ×r: хвіст біноміального розподілу."""
    return sum(comb(r, j) * p**j * (1 - p)**(r - j) for j in range((r + 1) // 2, r + 1))
