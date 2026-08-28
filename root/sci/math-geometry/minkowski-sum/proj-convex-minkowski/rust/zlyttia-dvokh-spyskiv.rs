/// Сума Мінковського двох опуклих багатокутників — O(m + n).
fn minkowski(mut a: Vec<Pt>, mut b: Vec<Pt>) -> Vec<Pt> {
    normalize(&mut a);
    normalize(&mut b);
    let (n, m) = (a.len(), b.len());

    let (a0, a1, b0, b1) = (a[0], a[1 % n], b[0], b[1 % m]);
    a.push(a0); a.push(a1);                // хвіст, щоб не брати індекси за модулем
    b.push(b0); b.push(b1);

    let mut res = Vec::with_capacity(n + m);
    let (mut i, mut j) = (0usize, 0usize);
    while i < n || j < m {
        res.push(a[i] + b[j]);
        let c = cross(a[i + 1] - a[i], b[j + 1] - b[j]);
        if c >= 0 && i < n { i += 1; }      // ребро A за напрямом не пізніше — беремо його
        if c <= 0 && j < m { j += 1; }      // ребро B за напрямом не пізніше — беремо його
    }
    res
}
