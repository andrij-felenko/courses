# Метод променя: чи точка (px, py) всередині багатокутника з вершинами verts.
# verts — список пар (x, y) на площині.
# Промінь пускаємо горизонтально праворуч; inside перемикається на кожному
# перетині сторони — фінальний стан і є відповідь (парність числа перетинів).
def point_in_polygon(px, py, verts):
    inside = False
    n = len(verts)
    j = n - 1
    for i in range(n):
        xi, yi = verts[i]
        xj, yj = verts[j]
        # Умова 1: сторона (verts[j] → verts[i]) накриває рівень py по вертикалі.
        straddles = (yi > py) != (yj > py)
        if straddles:
            # Умова 2: точка перетину сторони з горизонталлю лежить правіше px.
            x_cross = xi + (py - yi) * (xj - xi) / (yj - yi)
            if px < x_cross:
                inside = not inside      # перетин — перемкнути парність
        j = i
    return inside
