// два &mut в один зріз — через split_at_mut, ідіоматичний спосіб Rust
struct Body { x: f64, v: f64, m: f64, r: f64 }

fn resolve(bodies: &mut [Body], i: usize, j: usize, e: f64) {
    let (lo, hi) = (i.min(j), i.max(j));
    let (left, right) = bodies.split_at_mut(hi);
    let a = &mut left[lo];
    let b = &mut right[0];
    let vcm = (a.m*a.v + b.m*b.v) / (a.m + b.m);    // центр мас — його тримає Σp
    a.v = (1.0 + e)*vcm - e*a.v;
    b.v = (1.0 + e)*vcm - e*b.v;
}
