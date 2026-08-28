struct RowSource {                     // те, що вміє курсор драйвера
    virtual bool        next()                 = 0;
    virtual bool        is_null(size_t c) const = 0;
    virtual int64_t     as_int(size_t c) const = 0;
    virtual std::string as_text(size_t c) const = 0;
    virtual ~RowSource() = default;
};

void RecordSet::reserve(size_t n) {
    for (Column& k : cols_) {
        if (k.type == Type::Int64) k.i64.reserve(n); else k.txt.reserve(n);
        k.valid.reserve((n + 63) / 64);
    }
    state_.reserve(n);
}

size_t RecordSet::grow_one() {         // місце під новий рядок у ВСІХ масивах
    const size_t r = nrows_;
    for (Column& k : cols_) {
        if (k.type == Type::Int64) k.i64.emplace_back(); else k.txt.emplace_back();
        if ((r >> 6) >= k.valid.size()) k.valid.push_back(0);
        set_bit(k.valid, r, false);    // поки не записали — комірка порожня
    }
    state_.push_back(RowState::Unchanged);
    ++nrows_;
    return r;
}

void RecordSet::load(RowSource& src, size_t expect) {
    reserve(expect);
    while (src.next()) {
        const size_t r = grow_one();
        for (size_t c = 0; c < cols_.size(); ++c) {
            if (src.is_null(c)) continue;              // біт уже нульовий
            Column& k = cols_[c];
            if (k.type == Type::Int64) k.i64[r] = src.as_int(c);
            else                       k.txt[r] = src.as_text(c);
            set_bit(k.valid, r, true);
        }
    }
}
