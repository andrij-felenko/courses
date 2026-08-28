def hysteresis(nms, lo, hi):
    """Двопороговий гістерезис. nms — сила після NMS; повертає бінарний вихід (0/255).
    Стек на H*W позицій (найгірший випадок)."""
    WEAK, STRONG = 1, 2
    H, W = nms.shape
    mark = np.zeros((H, W), dtype=np.uint8)
    stack = []

    # 1) класифікація + засів стеку сильними
    for i in range(H):
        for j in range(W):
            if nms[i, j] >= hi:
                mark[i, j] = STRONG
                stack.append((i, j))
            elif nms[i, j] >= lo:
                mark[i, j] = WEAK
            # інакше mark лишається 0 (не межа)

    # 2) BFS від сильних: будь-який слабкий сусід стає сильним і йде в стек
    DY = (-1, -1, -1, 0, 0, 1, 1, 1)
    DX = (-1, 0, 1, -1, 1, -1, 0, 1)
    while stack:
        y, x = stack.pop()
        for k in range(8):
            ny, nx = y + DY[k], x + DX[k]
            if ny < 0 or nx < 0 or ny >= H or nx >= W:
                continue
            if mark[ny, nx] == WEAK:
                mark[ny, nx] = STRONG
                stack.append((ny, nx))

    # 3) вихід: лишилися тільки сильні (сильні від народження + дотягнуті слабкі)
    return np.where(mark == STRONG, 255, 0).astype(np.uint8)
