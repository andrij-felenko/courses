void RecordSet::accept() {
    for (size_t r = 0; r < nrows_; ++r) {
        if (state_[r] != RowState::Added) continue;
        for (Column& k : cols_)                       // тимчасові ключі стають справжніми
            if (k.key_ref && k.type == Type::Int64 && bit(k.valid, r))
                k.i64[r] = keys_->resolve(k.i64[r]);
    }
    orig_.clear();
    for (RowState& s : state_)
        if (s != RowState::Deleted && s != RowState::Discarded) s = RowState::Unchanged;
    compact();
}

void RecordSet::compact() {
    std::vector<size_t> keep;
    keep.reserve(nrows_);
    for (size_t r = 0; r < nrows_; ++r)
        if (state_[r] != RowState::Deleted && state_[r] != RowState::Discarded)
            keep.push_back(r);
    if (keep.size() == nrows_) return;                // прибирати нема чого

    for (Column& k : cols_) {
        std::vector<uint64_t> nv((keep.size() + 63) / 64, 0);
        for (size_t i = 0; i < keep.size(); ++i) {
            const size_t src = keep[i];               // src >= i завжди, тож рух уперед безпечний
            if (k.type == Type::Int64) k.i64[i] = k.i64[src];
            else                       k.txt[i] = std::move(k.txt[src]);
            set_bit(nv, i, bit(k.valid, src));
        }
        if (k.type == Type::Int64) k.i64.resize(keep.size());
        else                       k.txt.resize(keep.size());
        k.valid.swap(nv);
    }
    for (size_t i = 0; i < keep.size(); ++i) state_[i] = state_[keep[i]];
    state_.resize(keep.size());
    nrows_ = keep.size();
}
