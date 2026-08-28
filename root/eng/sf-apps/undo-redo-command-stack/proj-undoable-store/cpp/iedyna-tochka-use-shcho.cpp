void Store::begin(std::string label, std::string mergeKey) {
    if (open_)
        throw std::logic_error("вкладені транзакції заборонені: намір не буває всередині наміру");
    open_ = Open{ root_, sel_, std::move(label), std::move(mergeKey), g_born, 0 };
}

// Уся модель міняється ТІЛЬКИ тут. Немає другого шляху — і саме тому історія повна.
void Store::apply(const Edit& edit, Selection selAfter) {
    const bool implicit = !open_;             // проста дія — сама собі транзакція
    if (implicit) begin("зміна");
    try {
        EditResult r = edit(root_);           // ← усе, що здатне впасти, падає ТУТ
        root_ = std::move(r.root);            // ← присвоєння вказівника: не кине ніколи
        sel_  = selAfter;
        open_->removed += r.removed;
    } catch (...) {
        rollback();                           // намір не відбувся — стан на початок кроку
        throw;
    }
    notify_();                                // подання перемальовується вже зараз
    if (implicit) commit();
}

void Store::rollback() noexcept {
    if (!open_) return;
    root_ = open_->base;      // одне присвоєння — і все, що встигли побудувати, стає сміттям
    sel_  = open_->selBefore;
    open_.reset();
    notify_();                // ⚠ цей виклик мусить бути noexcept: виняток із відкату вб'є процес
}
