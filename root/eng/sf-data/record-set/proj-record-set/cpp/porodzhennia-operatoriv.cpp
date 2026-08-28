struct Statement {
    std::string        sql;
    std::vector<Value> params;
    size_t             returns_key_into = SIZE_MAX;   // рядок, чий ключ видасть база
};

Value RecordSet::param_at(size_t r, size_t c) const {
    Value v = value_at(r, c);
    if (cols_[c].key_ref)
        if (const int64_t* n = std::get_if<int64_t>(&v))
            v = keys_->resolve(*n);                   // тимчасовий ключ → справжній
    return v;
}

Value RecordSet::original_at(size_t r, size_t c) const {
    const auto it = orig_.find(cell_key(r, c));
    return (it == orig_.end()) ? value_at(r, c) : it->second;   // не правили — поточне і є початковим
}

std::string RecordSet::where_original(size_t r, std::vector<Value>& params) const {
    std::string w;
    for (size_t c = 0; c < cols_.size(); ++c) {
        if (!w.empty()) w += " AND ";
        const Value ov = original_at(r, c);
        if (std::holds_alternative<std::monostate>(ov)) {
            w += cols_[c].name + " IS NULL";          // «= NULL» не буває істинним НІКОЛИ
        } else {
            params.push_back(ov);
            w += cols_[c].name + " = $" + std::to_string(params.size());
        }
    }
    return w;
}

Statement RecordSet::make_update(size_t r) const {
    Statement st;
    std::string sets;
    for (size_t c = 0; c < cols_.size(); ++c) {
        if (orig_.find(cell_key(r, c)) == orig_.end()) continue;  // цю колонку не чіпали
        if (!sets.empty()) sets += ", ";
        st.params.push_back(param_at(r, c));                      // ПОТОЧНЕ значення
        sets += cols_[c].name + " = $" + std::to_string(st.params.size());
    }
    st.sql = "UPDATE " + table_ + " SET " + sets +
             " WHERE " + where_original(r, st.params);
    return st;
}

Statement RecordSet::make_delete(size_t r) const {
    Statement st;
    st.sql = "DELETE FROM " + table_ + " WHERE " + where_original(r, st.params);
    return st;
}

Statement RecordSet::make_insert(size_t r) const {
    Statement st;
    std::string names, marks;
    for (size_t c = 0; c < cols_.size(); ++c) {
        if (cols_[c].generated) continue;                         // ключ видасть база
        if (!names.empty()) { names += ", "; marks += ", "; }
        st.params.push_back(param_at(r, c));
        names += cols_[c].name;
        marks += "$" + std::to_string(st.params.size());
    }
    st.sql = "INSERT INTO " + table_ + " (" + names + ") VALUES (" + marks + ")";
    for (size_t i = 0; i < key_.size(); ++i)
        st.sql += (i ? ", " : " RETURNING ") + key_[i];
    st.returns_key_into = r;
    return st;
}
