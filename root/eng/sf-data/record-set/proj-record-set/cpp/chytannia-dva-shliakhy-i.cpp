bool RecordSet::is_null(size_t r, size_t c) const { return !bit(cols_[c].valid, r); }

std::optional<int64_t> RecordSet::get_int(size_t r, size_t c) const {
    const Column& k = cols_[c];
    if (!bit(k.valid, r)) return std::nullopt;
    return k.i64[r];
}

std::optional<std::string_view> RecordSet::get_text(size_t r, size_t c) const {
    const Column& k = cols_[c];
    if (!bit(k.valid, r)) return std::nullopt;
    return std::string_view(k.txt[r]);
}
