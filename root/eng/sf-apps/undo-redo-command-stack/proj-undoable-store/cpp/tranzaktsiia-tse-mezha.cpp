void Store::commit() {
    if (!open_) return;
    Open op = std::move(*open_);
    open_.reset();
    if (root_ == op.base) return;                     // нічого не змінилося — кроку не буде

    const std::size_t w = (g_born - op.born0) + op.removed;   // додане + вилучене
    const auto now = std::chrono::steady_clock::now();
    using namespace std::chrono_literals;

    const bool canMerge =
        !op.mergeKey.empty() &&
        index_ == steps_.size() &&                    // ми на кінці лінії, гілки повтору немає
        index_ > 0 &&
        steps_.back().mergeKey == op.mergeKey &&      // той самий намір, що й у сусіда
        now - steps_.back().at < 700ms &&             // серія не переривалася паузою
        saved_ != static_cast<long long>(index_);     // ← на цьому кроці стоїть точка збереження

    if (canMerge) {                                   // серія триває — розтягуємо останній крок
        Step& last = steps_.back();
        last.after    = root_;
        last.selAfter = sel_;
        last.weight  += w;
        last.at       = now;
        bytes_ += w;
        trim();
        return;
    }
    pushStep(Step{ op.base, root_, op.selBefore, sel_, std::move(op.label),
                   std::move(op.mergeKey), w, now });
}

// Межа наміру як об'єкт: поки живий — крок відкритий. Вихід із області видимості
// будь-яким шляхом (return, break, виняток) без commit() означає відкат.
class Intent {
public:
    Intent(Store& s, std::string label, std::string mergeKey = {}) : s_(s) {
        s_.begin(std::move(label), std::move(mergeKey));
    }
    ~Intent() { if (!done_) s_.rollback(); }
    void commit() { s_.commit(); done_ = true; }
    Intent(const Intent&) = delete;
    Intent& operator=(const Intent&) = delete;
private:
    Store& s_;
    bool   done_ = false;
};

// Три зміни моделі — один крок історії.
void formatParagraph(Store& store, const std::string& id, const Style& st) {
    Intent step(store, "оформлення абзацу");
    store.apply(setBold  (id, st.bold),   keepSelection(store));
    store.apply(setIndent(id, st.indent), keepSelection(store));
    store.apply(setAlign (id, st.align),  keepSelection(store));  // ← кине — деструктор поверне все
    step.commit();
}
