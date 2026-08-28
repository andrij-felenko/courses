fn prec(c: char) -> u8 {
    match c { '+' | '-' => 1, '*' | '/' => 2, _ => 0 }
}

fn tok_prec(t: Tok) -> u8 {
    match t { Tok::Op(c) => prec(c), _ => 0 }
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Tok { Num(i64), Op(char), LPar, RPar }

/// Інфікс → постфікс. Один прохід = одна дія.
fn to_rpn(tokens: &[Tok]) -> Vec<Tok> {
    let mut out: Vec<Tok> = Vec::new();
    let mut ops: Vec<Tok> = Vec::new();
    let mut i = 0usize;

    while i < tokens.len() || !ops.is_empty() {
        // варіант — ПАРА; кортежі в Rust порівнюються словниково «з коробки»
        let v = (tokens.len() - i, ops.len());

        let t = tokens.get(i).copied();
        let top = ops.last().copied();

        if let Some(n @ Tok::Num(_)) = t {
            out.push(n); i += 1;                             // число — одразу у вихід
        } else if t == Some(Tok::LPar) {
            ops.push(Tok::LPar); i += 1;
        } else if t == Some(Tok::RPar) && top == Some(Tok::LPar) {
            ops.pop(); i += 1;                               // дужка закрилася
        } else if let Some(Tok::Op(c)) = t {
            if top.map_or(true, |x| x == Tok::LPar || tok_prec(x) < prec(c)) {
                ops.push(Tok::Op(c)); i += 1;                // оператор іде вгору
            } else {
                out.push(ops.pop().unwrap());                // старший оператор — у вихід
            }
        } else {
            out.push(ops.pop().expect("незбалансовані дужки"));
        }

        debug_assert!((tokens.len() - i, ops.len()) < v);    // пара впала словниково
    }
    out
}
