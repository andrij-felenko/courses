/// Чи лежить q в опуклому CCW-багатокутнику v (межа рахується всередині). O(log n).
/// v уже нормалізований, тож v[0] — опорна вершина віяла.
fn point_in_convex(v: &[Pt], q: Pt) -> bool {
    let n = v.len();
    if n == 1 { return q == v[0]; }
    if n == 2 {                                     // вироджений випадок — відрізок
        let (d, e) = (v[1] - v[0], q - v[0]);
        let t = d.x * e.x + d.y * e.y;
        return cross(d, e) == 0 && t >= 0 && t <= d.x * d.x + d.y * d.y;
    }
    if cross(v[1] - v[0], q - v[0]) < 0 { return false; }      // поза віялом з одного боку
    if cross(v[n - 1] - v[0], q - v[0]) > 0 { return false; }  // ...і з другого

    let (mut lo, mut hi) = (1usize, n - 1);         // шукаємо сектор між lo та lo+1
    while hi - lo > 1 {
        let mid = (lo + hi) / 2;
        if cross(v[mid] - v[0], q - v[0]) >= 0 { lo = mid } else { hi = mid }
    }
    cross(v[hi] - v[lo], q - v[lo]) >= 0            // з внутрішнього боку ребра
}

/// Чи перетинаються два опуклі багатокутники.
fn convex_intersect(a: &[Pt], b: &[Pt]) -> bool {
    let mirrored: Vec<Pt> = b.iter().map(|&p| -p).collect();   // саме −B, а не зсув B
    point_in_convex(&minkowski(a.to_vec(), mirrored), Pt { x: 0, y: 0 })
}
