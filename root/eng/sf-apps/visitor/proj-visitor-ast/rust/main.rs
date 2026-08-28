use std::collections::HashMap;

enum Expr {
    Num(f64),
    Var(String),
    Neg(Box<Expr>),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
}

// «обчислювач» — проста функція; той самий обхід, лише без accept/visit
fn eval(e: &Expr, env: &HashMap<String, f64>) -> f64 {
    match e {
        Expr::Num(v)    => *v,
        Expr::Var(x)    => env[x],
        Expr::Neg(a)    => -eval(a, env),
        Expr::Add(l, r) => eval(l, env) + eval(r, env),
        Expr::Mul(l, r) => eval(l, env) * eval(r, env),
    }
}

// «лічильник» — інша функція, той самий розбір
fn count(e: &Expr) -> u32 {
    match e {
        Expr::Num(_) | Expr::Var(_)       => 1,
        Expr::Neg(a)                      => 1 + count(a),
        Expr::Add(l, r) | Expr::Mul(l, r) => 1 + count(l) + count(r),
    }
}
