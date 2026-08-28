class Store {
public:
    Store(State initial, Io& io) : state_(std::move(initial)), io_(io) {}

    void dispatch(Action a) {
        queue_.push_back(std::move(a));
        if (running_) return;          // цикл уже крутиться — він забере й цю дію
        running_ = true;

        while (!queue_.empty()) {
            Action cur = std::move(queue_.front());
            queue_.pop_front();

            log_.push_back(cur);                 // журнал: що прийшло і в якому порядку
            Step step = update(state_, cur);     // єдине місце, де народжується стан
            state_ = std::move(step.state);
            io_.paint(view(state_));             // рівно один кадр на завершену версію

            for (const Effect& e : step.effects) // dispatch звідси лише стає в чергу
                perform(e);
        }

        running_ = false;
    }

    const State&               state() const { return state_; }
    const std::vector<Action>& log()   const { return log_; }

private:
    void perform(const Effect& e) {
        std::visit(overload{
            [&](const FetchRate&) { io_.fetch_rate(*this); },
            [&](const Persist&)   { io_.persist(state_); },
            [&](const Retry& r)   { io_.retry_after(r.after_ms, *this); },
        }, e);
    }

    State               state_;
    std::deque<Action>  queue_;
    std::vector<Action> log_;
    bool                running_ = false;
    Io&                 io_;
};
