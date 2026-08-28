// ── 2. Похідний вузол ─────────────────────────────────────────────────
class Derived : public Node {
public:
    Derived* asDerived() override { return this; }

    std::vector<Node*> deps;   // кого читав ОСТАННЬОГО разу
    long markedAt  = 0;        // епоха, у якій позначено застарілим
    long settledAt = 0;        // епоха, у якій уже влігся

    bool recompute();
    void dispose() {           // зняти себе з усіх входів
        for (Node* d : deps) unlink(*d, *this);
        deps.clear();
    }

protected:
    virtual bool eval() = 0;   // виконати вираз; true — значення змінилося
    bool running = false;      // проти циклу в графі
    friend void track(Node&);
    friend class Frame;
};

/** RAII-рамка: хто зараз обчислюється — і повернення стану на будь-якому виході. */
class Frame {
public:
    explicit Frame(Derived& n) : prev_(frame), self_(n) { frame = &n; n.running = true; }
    ~Frame() { self_.running = false; frame = prev_; }
    Frame(const Frame&) = delete;
    Frame& operator=(const Frame&) = delete;
private:
    Derived* prev_;
    Derived& self_;
};

inline void track(Node& n) {
    if (!frame) return;                  // читання поза обчисленням нічого не підписує
    auto& d = frame->deps;
    if (std::find(d.begin(), d.end(), &n) != d.end()) return;   // те саме читали двічі
    d.push_back(&n);
    n.subs.push_back(frame);
}

inline bool Derived::recompute() {
    if (running) throw std::logic_error("цикл у графі: вузол читає сам себе");

    std::vector<Node*> before;
    before.swap(deps);

    bool changed;
    { Frame f(*this); changed = eval(); }   // ← поки живе f, читання реєструються на нас
                                            // (виняток звідси лишить пів набору — див. пастки)
    for (Node* d : before)                  // зняти те, чого цього разу НЕ читали
        if (std::find(deps.begin(), deps.end(), d) == deps.end())
            unlink(*d, *this);

    height = 0;
    for (Node* d : deps) height = std::max(height, d->height + 1);

    if (changed) changedAt = epoch;
    return changed;
}

template <class T>
class Computed final : public Derived {
public:
    using Eq = std::function<bool(const T&, const T&)>;

    explicit Computed(std::function<T()> fn, Eq eq = std::equal_to<T>{})
        : fn_(std::move(fn)), eq_(std::move(eq)) {}

    const T& get() {
        if (running) throw std::logic_error("цикл у графі: вузол читає сам себе");
        if (!fresh_) recompute();     // перше читання й заводить вузол у граф
        else settleNode(*this);       // до нас дійшли раніше за чергу — влягаємось тут-таки
        track(*this);
        return value_;
    }

protected:
    bool eval() override {
        T next = fn_();
        const bool changed = !fresh_ || !eq_(next, value_);
        value_ = std::move(next);
        fresh_ = true;
        return changed;
    }

private:
    std::function<T()> fn_;
    Eq   eq_;
    T    value_{};
    bool fresh_ = false;
};

/** Ефект — лист графа, що робить видиму роботу й нічого не віддає далі. */
class Effect final : public Derived {
public:
    explicit Effect(std::function<void()> fn) : fn_(std::move(fn)) { recompute(); }
    ~Effect() override { dispose(); }            // ← відписку не можна забути

    Effect(const Effect&) = delete;
    Effect& operator=(const Effect&) = delete;

protected:
    bool eval() override { fn_(); return false; }

private:
    std::function<void()> fn_;
};
