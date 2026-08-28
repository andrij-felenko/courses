// copy_probe.cpp — стенд для спостереження за усуненням копій
#include <cstdio>
#include <utility>

struct Probe {
    static int next_id, ctors, copies, moves, dtors;
    int id;

    Probe() : id(++next_id) {
        ++ctors;
        std::printf("    [%d] конструктор\n", id);
    }
    Probe(const Probe& src) : id(++next_id) {
        ++copies;
        std::printf("    [%d] КОПІЯ з [%d]\n", id, src.id);
    }
    Probe(Probe&& src) noexcept : id(++next_id) {
        ++moves;
        std::printf("    [%d] переміщення з [%d]\n", id, src.id);
    }
    ~Probe() {
        ++dtors;
        std::printf("    [%d] деструктор\n", id);
    }
};

int Probe::next_id = 0;
int Probe::ctors = 0;
int Probe::copies = 0;
int Probe::moves = 0;
int Probe::dtors = 0;

// ── шість сценаріїв повернення ───────────────────────────────────────

Probe urvo()               { return Probe(); }
Probe nrvo()               { Probe p; return p; }
Probe two_branches(bool c) { Probe a, b; if (c) return a; return b; }
Probe with_move()          { Probe p; return std::move(p); }

struct Box { Probe member; };
Probe from_field()         { Box b; return b.member; }

Probe const_local()        { const Probe p; return p; }

// ── чи справді комірка одна ──────────────────────────────────────────

Probe report_own_address(void** where) { Probe p; *where = &p; return p; }

// ── фабрика типу, що не копіюється й не переміщується ────────────────

#if __cplusplus >= 201703L
struct Latch {
    Latch()  { std::printf("    [L] конструктор\n"); }
    ~Latch() { std::printf("    [L] деструктор\n"); }
    Latch(const Latch&) = delete;
    Latch(Latch&&)      = delete;
};
Latch make_latch() { return Latch(); }
#endif

// ── обслуга стенду ───────────────────────────────────────────────────

static void start(const char* title, const char* code) {
    Probe::next_id = Probe::ctors = Probe::copies = 0;
    Probe::moves = Probe::dtors = 0;
    std::printf("\n=== %s   |   %s\n", title, code);
}

static void finish() {
    std::printf("    ─ об'єктів %d (звичайних %d, копій %d, переміщень %d), знищень %d\n",
                Probe::ctors + Probe::copies + Probe::moves,
                Probe::ctors, Probe::copies, Probe::moves, Probe::dtors);
}

int main() {
    std::printf("__cplusplus = %ld\n", (long)__cplusplus);

    start("1. безіменне значення (URVO)", "return Probe();");
    { Probe q = urvo();            (void)q; }
    finish();

    start("2. іменована локальна (NRVO)", "Probe p; return p;");
    { Probe q = nrvo();            (void)q; }
    finish();

    start("3. дві змінні на двох гілках", "if (c) return a; return b;");
    { Probe q = two_branches(true); (void)q; }
    finish();

    start("4. зайвий std::move", "return std::move(p);");
    { Probe q = with_move();       (void)q; }
    finish();

    start("5. повернення поля", "Box b; return b.member;");
    { Probe q = from_field();      (void)q; }
    finish();

    start("6. const-локальна", "const Probe p; return p;");
    { Probe q = const_local();     (void)q; }
    finish();

    start("7. одна комірка чи дві", "адреса локальної vs адреса q");
    {
        void* inside = nullptr;
        Probe q = report_own_address(&inside);
        std::printf("    локальна: %p, q: %p — %s\n",
                    inside, (void*)&q,
                    inside == (void*)&q ? "ТА САМА комірка" : "різні комірки");
    }
    finish();

#if __cplusplus >= 201703L
    std::printf("\n=== 8. фабрика типу без копіювання й переміщення (лише C++17)\n");
    { Latch l = make_latch();  (void)l; }
#else
    std::printf("\n=== 8. фабрика типу без копіювання й переміщення: у C++14 не збереться\n");
#endif
}
