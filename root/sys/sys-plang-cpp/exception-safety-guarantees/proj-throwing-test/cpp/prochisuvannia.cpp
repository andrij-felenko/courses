#include <cstdio>
#include <cstdlib>

// Перевірка, що не зникає під NDEBUG: assert тут був би пасткою.
inline void require(bool ok, const char* what, long long n) {
    if (ok) return;
    std::fprintf(stderr, "ПРОВАЛ на N = %lld: %s\n", n, what);
    std::exit(1);
}

// make   — будує свіжий піддослідний об'єкт
// op     — операція, гарантію якої перевіряють
// holds  — предикат інваріанта класу
// strong — чи вимагаємо ще й рівності зі знімком
template <class Make, class Op, class Holds>
long long sweep(Make make, Op op, Holds holds, bool strong) {
    constexpr long long kCap = 1000000;        // запобіжник від вічного циклу

    for (long long n = 1; n <= kCap; ++n) {
        const long long live0   = tally().live();
        const long long blocks0 = tally().blocks();
        bool threw = false;
        {
            wire().disarm();                   // збирання й знімок — поза грою
            auto subject = make();
            auto before  = subject;            // копія теж уміє кинути: не тут

            wire().arm(n);
            try { op(subject); }
            catch (const std::bad_alloc&) { threw = true; }
            wire().disarm();                   // перевіряти — уже без пастки

            if (threw) {
                require(holds(subject), "інваріант зламано", n);
                if (strong)
                    require(subject == before, "стан змінився попри сильну гарантію", n);
            }
        }                                      // ← тут гинуть subject і before
        require(tally().live()   == live0,   "лишилися живі елементи", n);
        require(tally().blocks() == blocks0, "лишився невивільнений блок", n);

        if (!threw) return n - 1;              // точки скінчилися: стільки їх було
    }
    require(false, "операція так і не пройшла цілою — чи не ковтає вона виняток?", kCap);
    return -1;
}
