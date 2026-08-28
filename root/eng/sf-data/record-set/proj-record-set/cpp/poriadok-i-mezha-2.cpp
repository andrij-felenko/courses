struct Result { int64_t affected = 0; std::vector<Value> returned; };

struct Db {
    virtual void   begin()    = 0;
    virtual void   commit()   = 0;
    virtual void   rollback() = 0;
    virtual Result execute(const std::string& sql, const std::vector<Value>& params) = 0;
    virtual ~Db() = default;
};

struct Conflict : std::runtime_error {
    Conflict(const std::string& sql, int64_t affected)
        : std::runtime_error("змінено рядків: " + std::to_string(affected) + "; " + sql) {}
};

// sets подано в порядку залежності: батьки раніше за дітей
void apply_all(Db& db, KeyBook& keys, const std::vector<RecordSet*>& sets) {
    std::vector<Op> plan;
    for (RecordSet* rs : sets)  rs->collect(plan, Phase::Insert);   // батьки → діти
    for (RecordSet* rs : sets)  rs->collect(plan, Phase::Update);
    for (auto it = sets.rbegin(); it != sets.rend(); ++it)          // діти → батьки
        (*it)->collect(plan, Phase::Delete);

    db.begin();
    try {
        for (const Op& op : plan) {
            const Statement st = op.set->make(op.row, op.phase);    // будуємо ТУТ, не раніше
            const Result res = db.execute(st.sql, st.params);
            if (res.affected != 1)
                throw Conflict(st.sql, res.affected);               // 0 — нас випередили
            if (st.returns_key_into != SIZE_MAX)
                op.set->note_key(st.returns_key_into, res.returned);
        }
        db.commit();
    } catch (...) {
        db.rollback();
        keys.real.clear();          // видані ключі більше нічого не означають
        throw;                      // стани рядків НЕ чіпаємо: правки лишаються в наборі
    }
    for (RecordSet* rs : sets) rs->accept();   // і лише тепер, після успішного COMMIT
}
