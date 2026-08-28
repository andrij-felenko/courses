enum Effect {
    SaveUser(User),
    AppendLedger { user_id: u64, amount: i64, at: i64 },
    Notify { to: String, text: String },
}

fn run(eff: Effect, db: &mut Db, mailer: &Mailer) {
    match eff {                        // додаси варіант — доки не обробиш його тут, не збереться
        Effect::SaveUser(u)                          => db.save_user(u),
        Effect::AppendLedger { user_id, amount, at } => db.append_ledger(user_id, amount, at),
        Effect::Notify { to, text }                  => mailer.send(&to, &text),
    }
}
