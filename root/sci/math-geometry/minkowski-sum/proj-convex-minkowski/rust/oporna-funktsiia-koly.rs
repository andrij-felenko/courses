/// Найдальша точка багатокутника в напрямі u. Строге «>» — щоб за рівності
/// відповідь була та сама, інакше GJK зациклиться на перпендикулярному ребрі.
fn far(v: &[Pt], u: Pt) -> Pt {
    let mut best = v[0];
    let mut best_dot = v[0].x * u.x + v[0].y * u.y;
    for &p in v.iter().skip(1) {
        let d = p.x * u.x + p.y * u.y;
        if d > best_dot { best_dot = d; best = p; }
    }
    best
}

/// Опорна точка множини різниць A ⊕ (−B) — без побудови самої множини.
fn support(a: &[Pt], b: &[Pt], u: Pt) -> Pt { far(a, u) - far(b, -u) }

fn main() {
    let tri = vec![Pt { x: 0, y: 0 }, Pt { x: 4, y: 0 }, Pt { x: 0, y: 3 }];
    let sq = vec![Pt { x: 0, y: 0 }, Pt { x: 1, y: 0 },
                  Pt { x: 1, y: 1 }, Pt { x: 0, y: 1 }];

    for p in minkowski(tri.clone(), sq.clone()) { print!("({},{}) ", p.x, p.y); }
    println!();

    // той самий трикутник, зсунутий убік
    let away: Vec<Pt> = tri.iter().map(|&p| p + Pt { x: 10, y: 0 }).collect();
    println!("{} {}", convex_intersect(&tri, &sq), convex_intersect(&tri, &away));
}
