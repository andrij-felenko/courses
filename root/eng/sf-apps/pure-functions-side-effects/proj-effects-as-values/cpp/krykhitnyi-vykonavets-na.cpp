// ВИКОНАВЕЦЬ: намір → справжній ефект. std::visit розгалужує за активним варіантом.
template<class... Ts> struct overload : Ts... { using Ts::operator()...; };
template<class... Ts> overload(Ts...) -> overload<Ts...>;

void run(const Effect& eff, Database& db, Mailer& mailer) {
    std::visit(overload{
        [&](const SaveUser& e)     { db.saveUser(e.user); },
        [&](const AppendLedger& e) { db.appendLedger(e.userId, e.amount, e.at); },
        [&](const Notify& e)       { mailer.send(e.to, e.text); },
    }, eff);
}

// ОБОЛОНКА: принести дані → спитати ядро → прокрутити план. Нуль рішень.
void claimBonus(int userId, Deps& deps) {
    User user = deps.db.loadUser(userId);
    auto plan = decideBonus(user, deps.clock(), deps.rng(), deps.cfg);
    for (const Effect& eff : plan) run(eff, deps.db, deps.mailer);
}
