class NaiveStore {                        // ← так робити не треба
public:
    void dispatch(const Action& a) {
        Step step = update(state_, a);
        state_ = std::move(step.state);
        io_.paint(view(state_));
        for (const Effect& e : step.effects) perform(e);   // ← perform кличе dispatch
    }
private:
    void perform(const Effect& e);
    State state_;
    Io&   io_;
};
