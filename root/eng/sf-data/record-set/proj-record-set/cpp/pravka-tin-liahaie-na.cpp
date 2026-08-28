Value RecordSet::value_at(size_t r, size_t c) const {
    const Column& k = cols_[c];
    if (!bit(k.valid, r)) return std::monostate{};
    return (k.type == Type::Int64) ? Value{k.i64[r]} : Value{k.txt[r]};
}

void RecordSet::remember(size_t r, size_t c) {
    if (state_[r] == RowState::Added) return;      // початкових значень у нього немає
    const uint64_t key = cell_key(r, c);
    if (orig_.find(key) != orig_.end()) return;    // тінь кладемо лише на ПЕРШУ правку
    orig_.emplace(key, value_at(r, c));
}

void RecordSet::set_int(size_t r, size_t c, std::optional<int64_t> v) {
    remember(r, c);
    Column& k = cols_[c];
    if (v) k.i64[r] = *v;
    set_bit(k.valid, r, v.has_value());
    if (state_[r] == RowState::Unchanged) state_[r] = RowState::Modified;
}

void RecordSet::set_text(size_t r, size_t c, std::optional<std::string> v) {
    remember(r, c);
    Column& k = cols_[c];
    if (v) k.txt[r] = std::move(*v);
    set_bit(k.valid, r, v.has_value());
    if (state_[r] == RowState::Unchanged) state_[r] = RowState::Modified;
}

size_t RecordSet::append_row() {
    const size_t r = grow_one();
    state_[r] = RowState::Added;
    for (Column& k : cols_)
        if (k.generated && k.type == Type::Int64) {
            k.i64[r] = keys_->issue();             // від'ємний тимчасовий ключ
            set_bit(k.valid, r, true);
        }
    return r;
}

void RecordSet::erase_row(size_t r) {
    state_[r] = (state_[r] == RowState::Added) ? RowState::Discarded
                                               : RowState::Deleted;
}
