void Store::pushStep(Step st) {
    // 1. Зріз гілки повтору: після нової дії старе майбутнє недосяжне
    while (steps_.size() > index_) {
        bytes_ -= steps_.back().weight;
        retire(std::move(steps_.back()));    // гине after зрізаних кроків → звільняється ДОДАНЕ
        steps_.pop_back();
    }
    if (saved_ > static_cast<long long>(index_))
        saved_ = -1;                         // точка збереження була в зрізаному — уже недосяжна

    // 2. Новий крок
    bytes_ += st.weight;
    steps_.push_back(std::move(st));
    ++index_;

    // 3. Бюджет
    trim();
}

bool Store::undo() {
    if (open_) return false;         // усередині незавершеного наміру відкочувати нема чого
    if (index_ == 0) return false;
    const Step& s = steps_[index_ - 1];
    root_ = s.before;                // ← ВЕСЬ відкат: одне присвоєння вказівника
    sel_  = s.selBefore;             // ← і людина опиняється там, де діяла
    --index_;
    notify_();
    return true;
}

bool Store::redo() {
    if (open_ || index_ >= steps_.size()) return false;
    const Step& s = steps_[index_];
    root_ = s.after;
    sel_  = s.selAfter;
    ++index_;
    notify_();
    return true;
}
