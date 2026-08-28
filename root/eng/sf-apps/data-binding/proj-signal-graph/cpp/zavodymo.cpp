// ── 4. Демонстрація ───────────────────────────────────────────────────
int main() {
    using namespace sg;

    Signal<int> s{1}, t{10};
    int cp = 0, cq = 0, cu = 0, cr = 0, cw = 0, ce = 0;

    Computed<int>  p{[&] { ++cp; return s.get() * 2; }};
    Computed<bool> q{[&] { ++cq; return s.get() > 0; }};
    Computed<int>  u{[&] { ++cu; return t.get() + 1; }};
    Computed<std::string> r{[&] {
        ++cr;
        return std::to_string(p.get()) + (q.get() ? " / так" : " / ні");
    }};
    Computed<int>  w{[&] { ++cw; return q.get() ? u.get() : 0; }};

    Effect show{[&] { ++ce; std::printf("r = %s\n", r.get().c_str()); }};
    w.get();          // перше читання й заводить w у граф (підписників у нього немає)

    s.set(5);         // p, q, r, ефект — перераховано; w пропущено
    t.set(20);        // тільки u і w; r та ефект не торкнуто взагалі
    s.set(-3);        // q стало false → w пішло іншою гілкою й ВІДПУСТИЛО u
    t.set(99);        // u перерахувалося — але вже ні для кого

    std::printf("p·%d q·%d u·%d r·%d w·%d ефект·%d\n", cp, cq, cu, cr, cw, ce);
}   // ← деструктор show зняв підписку
