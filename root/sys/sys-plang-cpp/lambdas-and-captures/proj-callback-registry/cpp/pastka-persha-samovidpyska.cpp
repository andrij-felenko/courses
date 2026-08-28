#include <algorithm>   // std::remove_if

class Subscription;    // повне визначення — нижче

class EventBus {
public:
    using Handler = std::function<void(const Tick&)>;
    using Id = std::size_t;

    Id subscribe(Handler h) {
        const Id id = next_++;
        std::vector<Slot>& target = (depth_ == 0) ? slots_ : pending_;
        target.push_back(Slot{id, true, std::move(h)});
        return id;
    }

    void unsubscribe(Id id) {
        if (!markDead(slots_, id)) markDead(pending_, id);
        if (depth_ == 0) flush();
    }

    void publish(const Tick& ev) {
        ++depth_;
        const std::size_t n = slots_.size();   // підписки, створені зараз, чекають наступної події
        for (std::size_t i = 0; i < n; ++i)
            if (slots_[i].alive) slots_[i].handler(ev);
        if (--depth_ == 0) flush();
    }

    [[nodiscard]] Subscription connect(Handler h);

private:
    struct Slot { Id id; bool alive; Handler handler; };

    static bool markDead(std::vector<Slot>& v, Id id) {
        for (Slot& s : v)
            if (s.id == id && s.alive) { s.alive = false; return true; }
        return false;
    }

    void flush() {
        slots_.erase(std::remove_if(slots_.begin(), slots_.end(),
                                    [](const Slot& s) { return !s.alive; }),
                     slots_.end());
        for (Slot& s : pending_)
            if (s.alive) slots_.push_back(std::move(s));
        pending_.clear();
    }

    std::vector<Slot> slots_;
    std::vector<Slot> pending_;
    Id next_ = 1;
    int depth_ = 0;
};
