struct Event {
    uint64_t at;  // віртуальний час спрацювання
    uint64_t seq; // номер народження — детермінований розрив нічиїх
    std::function<void()> fn;
};

// priority_queue — max-купа, тож компаратор інвертований: «пізніший = нижчий
// пріоритет». Так найраніший at спливає першим, а за рівного at вирішує менший seq.
struct Later {
    bool operator()(const Event& a, const Event& b) const {
        if (a.at != b.at) return a.at > b.at;
        return a.seq > b.seq; // однаковий час → вирішує seq, а не випадковість
    }
};

struct Sim {
    uint64_t now = 0;
    uint64_t seq = 0;
    Rand rng;
    std::priority_queue<Event, std::vector<Event>, Later> q;

    explicit Sim(uint64_t seed) : rng(seed) {}

    // after — запланувати fn через delay одиниць віртуального часу.
    void after(uint64_t delay, std::function<void()> fn) {
        ++seq;
        q.push(Event{now + delay, seq, std::move(fn)});
    }

    // run — головний цикл: доки є події, брати найранішу, посувати годинник, виконувати.
    void run() {
        while (!q.empty()) {
            Event e = q.top();
            q.pop();
            now = e.at; // годинник СТРИБАЄ прямо на час події — жодного реального очікування
            e.fn();
        }
    }
};
