N = 5                               # усереднюємо по 5 останніх інтервалів
g_intervals = [0] * N
g_idx = 0
g_prevBeat = 0
g_haveFirst = False

# Викликати в мить кожного зарахованого удару (now — його час).
def compute_bpm(now):
    global g_idx, g_prevBeat, g_haveFirst
    if not g_haveFirst:             # перший удар: інтервалу ще нема
        g_prevBeat = now
        g_haveFirst = True
        return 0                    # ще нема що рахувати
    beat_ms = now - g_prevBeat
    g_prevBeat = now

    # Відкидаємо явно хибні інтервали (поза людським діапазоном 30..240 уд/хв).
    if beat_ms < 250 or beat_ms > 2000:
        return -1                   # -1 = «підозрілий удар, пропускаємо»

    g_intervals[g_idx] = beat_ms
    g_idx = (g_idx + 1) % N

    # Середній інтервал по заповнених комірках → BPM.
    filled = [x for x in g_intervals if x > 0]
    if not filled:
        return 0
    return 60000 // (sum(filled) // len(filled))
