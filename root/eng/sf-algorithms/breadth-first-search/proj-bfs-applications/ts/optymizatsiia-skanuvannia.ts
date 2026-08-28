function floodFillTS(image: number[][], start_r: number, start_c: number, new_color: number): void {
    const rows = image.length;
    const cols = image[0].length;
    const target_color = image[start_r][start_c];
    if (target_color === new_color) return;

    const queue: [number, number][] = [[start_r, start_c]];
    image[start_r][start_c] = new_color;

    const dr = [-1, 1, 0, 0];
    const dc = [0, 0, -1, 1];
    let head = 0;

    while (head < queue.length) {
        const [r, c] = queue[head++];
        for (let i = 0; i < 4; i++) {
            const nr = r + dr[i];
            const nc = c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && image[nr][nc] === target_color) {
                image[nr][nc] = new_color;
                queue.push([nr, nc]);
            }
        }
    }
}
