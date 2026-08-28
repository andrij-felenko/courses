#[derive(Clone)]
enum Nat {
    Zero,
    Succ(Box<Nat>),             // Box: без непрямості тип мав би нескінченний розмір
}
use Nat::{Zero, Succ};

fn to_int(n: &Nat) -> u64 {
    match n {
        Zero => 0,
        Succ(pred) => 1 + to_int(pred),
    }
}

fn from_int(n: u64) -> Nat {
    match n {
        0 => Zero,
        _ => Succ(Box::new(from_int(n - 1))),
    }
}

fn add(a: &Nat, b: &Nat) -> Nat {
    match b {
        Zero => a.clone(),                       // a + 0 = a
        Succ(pred) => Succ(Box::new(add(a, pred))),
    }
}

fn mul(a: &Nat, b: &Nat) -> Nat {
    match b {
        Zero => Zero,                            // a · 0 = 0
        Succ(pred) => add(&mul(a, pred), a),     // a·S(b) = a·b + a
    }
}
