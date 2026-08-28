from collections import deque

def bfs_grid_python(grid: list[str], start: tuple[int, int], target: tuple[int, int]) -> int:
    rows, cols = len(grid), len(grid[0])
    if grid[start[0]][start[1]] == '#' or grid[target[0]][target[1]] == '#':
        return -1

    dist = [[-1] * cols for _ in range(rows)]
    q = deque([start])
    dist[start[0]][start[1]] = 0

    dr = [-1, 1, 0, 0]
    dc = [0, 0, -1, 1]

    while q:
        r, c = q.popleft()
        if (r, c) == target:
            return dist[r][c]

        for i in range(4):
            nr, nc = r + dr[i], c + dc[i]
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#' and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))

    return -1
