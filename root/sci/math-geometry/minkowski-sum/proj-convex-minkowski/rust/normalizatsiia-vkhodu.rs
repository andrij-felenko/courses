#[derive(Clone, Copy, PartialEq, Eq, Debug)]
struct Pt { x: i64, y: i64 }

impl std::ops::Add for Pt {
    type Output = Pt;
    fn add(self, o: Pt) -> Pt { Pt { x: self.x + o.x, y: self.y + o.y } }
}
impl std::ops::Sub for Pt {
    type Output = Pt;
    fn sub(self, o: Pt) -> Pt { Pt { x: self.x - o.x, y: self.y - o.y } }
}
impl std::ops::Neg for Pt {
    type Output = Pt;
    fn neg(self) -> Pt { Pt { x: -self.x, y: -self.y } }
}

/// z-складова векторного добутку: >0 — b лівіше a, <0 — правіше, 0 — той самий напрям
fn cross(a: Pt, b: Pt) -> i64 { a.x * b.y - a.y * b.x }

/// Без повторів і вершин посеред ребра, обхід проти годинникової стрілки,
/// вершина 0 — найнижча, а серед рівних — найлівіша.
fn normalize(p: &mut Vec<Pt>) {
    if p.is_empty() { return; }
    p.dedup();
    while p.len() > 1 && p[0] == p[p.len() - 1] { p.pop(); }

    let n = p.len();                            // подвоєна орієнтована площа
    let area2: i64 = (0..n).map(|i| cross(p[i], p[(i + 1) % n])).sum();
    if area2 < 0 { p.reverse(); }               // ==0 — точка або відрізок, лишаємо

    if p.len() > 2 {                            // викинути вершини всередині ребра
        let mut r: Vec<Pt> = Vec::with_capacity(p.len());
        for &v in p.iter() {
            while r.len() >= 2
                && cross(r[r.len() - 1] - r[r.len() - 2], v - r[r.len() - 1]) == 0 {
                r.pop();
            }
            r.push(v);
        }
        while r.len() > 2
            && cross(r[r.len() - 1] - r[r.len() - 2], r[0] - r[r.len() - 1]) == 0 { r.pop(); }
        while r.len() > 2
            && cross(r[0] - r[r.len() - 1], r[1] - r[0]) == 0 { r.remove(0); }
        *p = r;
    }

    let k = (0..p.len()).min_by_key(|&i| (p[i].y, p[i].x)).unwrap();
    p.rotate_left(k);
}
