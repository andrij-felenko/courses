function isBipartiteTS(adj: number[][]): boolean {
    const n = adj.length;
    const color = Array(n).fill(0);

    for (let start = 0; start < n; start++) {
        if (color[start] !== 0) continue;

        const queue: number[] = [start];
        color[start] = 1;
        let head = 0;

        while (head < queue.length) {
            const u = queue[head++];
            for (const v of adj[u]) {
                if (color[v] === 0) {
                    color[v] = 3 - color[u];
                    queue.push(v);
                } else if (color[v] === color[u]) {
                    return false;
                }
            }
        }
    }
    return true;
}
