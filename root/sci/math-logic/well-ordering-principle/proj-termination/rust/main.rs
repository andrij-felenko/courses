enum Expr {
    Num(i64),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
}

fn eval(e: &Expr) -> i64 {
    match e {
        Expr::Num(v) => *v,                     // база: лист, глибше не йдемо
        Expr::Add(l, r) => eval(l) + eval(r),   // виклики на власних піддеревах —
        Expr::Mul(l, r) => eval(l) * eval(r),   // кожне строго менше за e
    }
}
