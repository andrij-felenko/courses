struct Op { RecordSet* set; size_t row; Phase phase; };

void RecordSet::collect(std::vector<Op>& plan, Phase phase) {
    for (size_t r = 0; r < nrows_; ++r) {
        const bool take =
            (state_[r] == RowState::Added    && phase == Phase::Insert) ||
            (state_[r] == RowState::Modified && phase == Phase::Update) ||
            (state_[r] == RowState::Deleted  && phase == Phase::Delete);
        if (take) plan.push_back(Op{this, r, phase});
        // Unchanged і Discarded не дають нічого в жодній фазі
    }
}

Statement RecordSet::make(size_t r, Phase phase) const {
    switch (phase) {
        case Phase::Insert: return make_insert(r);
        case Phase::Update: return make_update(r);
        default:            return make_delete(r);
    }
}

void RecordSet::note_key(size_t r, const std::vector<Value>& returned) {
    for (size_t i = 0; i < key_.size() && i < returned.size(); ++i) {
        const size_t c = col(key_[i]);
        const int64_t* issued = std::get_if<int64_t>(&returned[i]);
        if (issued && cols_[c].type == Type::Int64)
            keys_->real[cols_[c].i64[r]] = *issued;  // тимчасовий ключ рядка → справжній
    }
}
