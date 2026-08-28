def dead_blocks_interleaved(errors, L=100, t=4, depth=10):
    """Те саме, але між каналом і кодом — перемішувач глибини D.
       Символ ефіру j належить слову (j % D) на позиції (j // D)."""
    dead = 0
    span = depth * L                       # надблок: D слів, перемішаних разом
    for base in range(0, len(errors) - span + 1, span):
        counts = [0] * depth
        for j in range(span):
            counts[j % depth] += errors[base + j]
        dead += sum(c > t for c in counts)
    return dead
