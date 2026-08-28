function bidirectionalBfsTS(adj: number[][], start: number, target: number): number {
    if (start === target) return 0;
    const n = adj.length;

    const dist_f = Array(n).fill(-1);
    const dist_b = Array(n).fill(-1);
    const q_f = [start], q_b = [target];
    dist_f[start] = 0; dist_b[target] = 0;

    let head_f = 0, head_b = 0;

    while (head_f < q_f.length && head_b < q_b.length) {
        const u_f = q_f[head_f++];
        for (const v of adj[u_f]) {
            if (dist_b[v] !== -1) return dist_f[u_f] + 1 + dist_b[v];
            if (dist_f[v] === -1) {
                dist_f[v] = dist_f[u_f] + 1;
                q_f.push(v);
            }
        }

        const u_b = q_b[head_b++];
        for (const v of adj[u_b]) {
            if (dist_f[v] !== -1) return dist_b[u_b] + 1 + dist_f[v];
            if (dist_f[v] === -1) {
                dist_f[v] = dist_b[u_b] + 1;
                q_b.push(v);
            }
        }
    }
    return -1;
}
