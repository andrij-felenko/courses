def encode(data):
    """data — R рядків по C бітів (0/1). Повертає кодове слово (R+1)×(C+1)."""
    R, C = len(data), len(data[0])
    w = [list(row) + [0] for row in data]   # копія даних + місце під парність рядка
    w.append([0] * (C + 1))                 # порожня стрічка парності стовпців

    for r in range(R):                      # парність кожного рядка даних
        p = 0
        for c in range(C):
            p ^= w[r][c]
        w[r][C] = p

    for c in range(C + 1):                  # парність кожного стовпця...
        p = 0
        for r in range(R):
            p ^= w[r][c]
        w[R][c] = p                         # ...а на c == C це вже кут

    return w
