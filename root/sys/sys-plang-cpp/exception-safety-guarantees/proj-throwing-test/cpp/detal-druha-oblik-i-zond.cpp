// Чотири числа, а не одне — про це нижче.
struct Ledger {
    long long built = 0, killed = 0;   // конструкції й деструкції елементів
    long long taken = 0, given = 0;    // виділені й звільнені блоки пам'яті
    long long live()   const { return built - killed; }
    long long blocks() const { return taken - given; }
};

inline Ledger& tally() { static Ledger l; return l; }

// Елемент-зонд: кожна дія, здатна кинути в справжньому типі,
// проходить через розтяжку. Деструктор — ніколи.
template <bool NothrowMove>
class Probe {
    int v_;
public:
    explicit Probe(int v = 0) : v_(v)    { wire().tick(); ++tally().built; }
    Probe(const Probe& o)     : v_(o.v_) { wire().tick(); ++tally().built; }

    Probe(Probe&& o) noexcept(NothrowMove) : v_(o.v_) {
        if constexpr (!NothrowMove) wire().tick();
        ++tally().built;
    }

    Probe& operator=(const Probe& o) { wire().tick(); v_ = o.v_; return *this; }

    Probe& operator=(Probe&& o) noexcept(NothrowMove) {
        if constexpr (!NothrowMove) wire().tick();
        v_ = o.v_;
        return *this;
    }

    ~Probe() { ++tally().killed; }

    // Порівняння без побічних дій і без тику — ним звірятимуть знімок.
    friend bool operator==(const Probe& a, const Probe& b) { return a.v_ == b.v_; }
    friend bool operator!=(const Probe& a, const Probe& b) { return !(a == b); }
};
