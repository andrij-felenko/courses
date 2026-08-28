function bfsGridTS(grid: string[], start: [number, number], target: [number, number]): number {
    const rows = grid.length;
    const cols = grid[0].length;
    if (grid[start[0]][start[1]] === '#' || grid[target[0]][target[1]] === '#') return -1;

    const dist: number[][] = Array.from({ length: rows }, () => Array(cols).fill(-1));
    const queue: [number, number][] = [start];
    dist[start[0]][start[1]] = 0;

    const dr = [-1, 1, 0, 0];
    const dc = [0, 0, -1, 1];
    let head = 0;

    while (head < queue.length) {
        const [r, c] = queue[head++];
        if (r === target[0] && c === target[1]) return dist[r][c];

        for (let i = 0; i < 4; i++) {
            const nr = r + dr[i];
            const nc = c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                grid[nr][nc] !== '#' && dist[nr][nc] === -1) {
                dist[nr][nc] = dist[r][c] + 1;
                queue.push([nr, nc]);
            }
        }
    }
    return -1;
}
