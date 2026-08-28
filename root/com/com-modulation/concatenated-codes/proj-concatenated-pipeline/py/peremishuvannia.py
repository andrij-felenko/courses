DEPTH = 8                         # скільки слів RS живе в одному блоці

def interleave(rows):
    """Пишемо рядками (слово = рядок), читаємо стовпцями."""
    return [rows[r][c] for c in range(N) for r in range(DEPTH)]

def deinterleave(stream):
    rows = [[0] * N for _ in range(DEPTH)]
    for i, b in enumerate(stream):
        rows[i % DEPTH][i // DEPTH] = b
    return rows

def flat(rows):                   # «без перемішування» — слово за словом
    return [b for row in rows for b in row]

def unflat(stream):
    return [stream[r * N:(r + 1) * N] for r in range(DEPTH)]
