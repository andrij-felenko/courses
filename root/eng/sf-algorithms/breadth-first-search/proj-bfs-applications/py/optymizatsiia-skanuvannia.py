from collections import deque

def flood_fill_python(image: list[list[int]], start_r: int, start_c: int, new_color: int) -> None:
    rows, cols = len(image), len(image[0])
    target_color = image[start_r][start_c]
    if target_color == new_color:
        return

    q = deque([(start_r, start_c)])
    image[start_r][start_c] = new_color

    dr = [-1, 1, 0, 0]
    dc = [0, 0, -1, 1]

    while q:
        r, c = q.popleft()
        for i in range(4):
            nr, nc = r + dr[i], c + dc[i]
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == target_color:
                image[nr][nc] = new_color
                q.append((nr, nc))
