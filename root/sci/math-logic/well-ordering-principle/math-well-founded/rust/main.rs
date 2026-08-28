enum Expr {
    Num(i64),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
}

fn ev(e: &Expr) -> i64 {
    match e {
        Expr::Num(v)    => *v,               // лист — база згортається сюди
        Expr::Add(l, r) => ev(l) + ev(r),    // рекурсія на власних піддеревах
        Expr::Mul(l, r) => ev(l) * ev(r),
    }
}
