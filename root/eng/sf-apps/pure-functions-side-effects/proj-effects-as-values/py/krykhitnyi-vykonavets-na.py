# ВИКОНАВЕЦЬ: намір → справжній ефект. Жодних рішень, лише розбір за типом.
def run(eff: Effect, db: Db, mailer: Mailer) -> None:
    match eff:
        case SaveUser(user):              db.save_user(user)
        case AppendLedger(uid, amt, at):  db.append_ledger(uid, amt, at)
        case Notify(to, text):            mailer.send(to, text)

# ОБОЛОНКА: принести дані → спитати ядро → прокрутити план. Три рядки, нуль рішень.
def claim_bonus(user_id: int, deps: Deps) -> None:
    user = deps.db.load_user(user_id)
    plan = decide_bonus(user, deps.clock(), deps.rng(), deps.cfg)
    for eff in plan:
        run(eff, deps.db, deps.mailer)
