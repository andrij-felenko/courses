// Набір лямбд як один викликаний об'єкт — типовий супутник std::visit
template <class... Fs> struct overload : Fs... { using Fs::operator()...; };
template <class... Fs> overload(Fs...) -> overload<Fs...>;

struct Step {
    State               state;    // нова версія стану
    std::vector<Effect> effects;  // що просимо зробити оболонку
};

Step update(const State& s, const Action& a) {
    Step step{ s, {} };      // копія старого стану — її й правимо
    State& n = step.state;

    std::visit(overload{
        [&](const Typed& t) {
            n.entered = t.field;
            n.amount  = t.amount;
            n.note.clear();
            step.effects.push_back(Persist{});
        },
        [&](const RateAsked&) {
            if (n.pending) return;            // запит уже в дорозі, другий не потрібен
            n.pending = true;
            n.note    = "оновлюю курс…";
            step.effects.push_back(FetchRate{});
        },
        [&](const RateCame& r) {
            n.pending = false;
            n.rate    = r.rate;
            n.note.clear();
            step.effects.push_back(Persist{});
        },
        [&](const RateFailed& f) {
            n.pending = false;
            n.note    = "курс не приїхав: " + f.why;
            step.effects.push_back(Retry{ 3000 });
        },
    }, a);

    return step;
}
