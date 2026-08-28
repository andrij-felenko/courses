// ── I. Повернення ─────────────────────────────────────────────────────────
static const Loud& forward_ref(const Loud& v) { return v; }   // сама по собі чесна

static void dangle_return() {
    head("висяче: повернення");
    const Loud& r = forward_ref(Loud("повернений"));
    std::cout << "    читаємо через висяче посилання...\n";
    std::cout << "    ім'я: " << r.name() << '\n';            // ← тут спиняє ASan
}

// ── II. Параметр ──────────────────────────────────────────────────────────
static const Loud* remembered = nullptr;
static void remember(const Loud& v) { remembered = &v; }

static void dangle_param() {
    head("висяче: параметр");
    remember(Loud("запам'ятований"));
    std::cout << "    тимчасовий уже знищено, а покажчик лишився\n";
    std::cout << "    ім'я: " << remembered->name() << '\n';   // ← тут спиняє ASan
}

// ── III. Ініціалізатор у new ──────────────────────────────────────────────
struct Watcher {                 // агрегат із полем-посиланням
    const Loud& target;
    int         weight;
};

static void dangle_new() {
    head("висяче: ініціалізатор у new");
    {   // на стеку ті самі фігурні дужки ПОДОВЖУЮТЬ життя тимчасового
        Watcher onStack{ Loud("на-стеку"), 1 };
        std::cout << "    на стеку: " << onStack.target.name()
                  << " × " << onStack.weight << "  (усе гаразд)\n";
    }
    Watcher* onHeap = new Watcher{ Loud("під-new-у-купі"), 2 };
    std::cout << "    у купі: тимчасовий уже знищено\n";
    std::cout << "    ім'я: " << onHeap->target.name() << '\n'; // ← тут спиняє ASan
    delete onHeap;
}

// ── IV. Список ініціалізації конструктора ─────────────────────────────────
class Keeper {
public:
    explicit Keeper(const Loud& v) : target_(v) {}   // законно й нічого не подовжує
    const Loud& target() const { return target_; }
private:
    const Loud& target_;
};

static void dangle_member() {
    head("висяче: поле-посилання");
    Keeper k(Loud("у-полі-об'єкта"));
    std::cout << "    конструктор відпрацював, тимчасовий знищено\n";
    std::cout << "    ім'я: " << k.target().name() << '\n';    // ← тут спиняє ASan
}

// ── V. Метод без ref-кваліфікатора ────────────────────────────────────────
class BadBuffer {
public:
    explicit BadBuffer(std::string tag) : payload_(std::move(tag)) {}
    const Loud& payload() const { return payload_; }   // приймає і тимчасовий об'єкт
private:
    Loud payload_;
};

static void dangle_method() {
    head("висяче: метод без ref-кваліфікатора");
    {   // з ref-кваліфікатором той самий за формою рядок безпечний
        const Loud& good = makeBuffer("із-кваліфікатором").payload();
        std::cout << "    із кваліфікатором: " << good.name() << "  (усе гаразд)\n";
    }
    const Loud& bad = BadBuffer("без-кваліфікатора").payload();
    std::cout << "    без кваліфікатора: тимчасовий буфер уже знищено\n";
    std::cout << "    ім'я: " << bad.name() << '\n';           // ← тут спиняє ASan
}

int main(int argc, char** argv) {
    const std::string mode = (argc > 1) ? argv[1] : "safe";

    if (mode == "safe") {
        part_overloads();
        part_lifetime();
        part_materialization();
        part_ref_qualifier();
        part_thread();
    }
    else if (mode == "return") dangle_return();
    else if (mode == "param")  dangle_param();
    else if (mode == "new")    dangle_new();
    else if (mode == "member") dangle_member();
    else if (mode == "method") dangle_method();
    else {
        std::cerr << "дослід: safe | return | param | new | member | method\n";
        return 2;
    }
    return 0;
}
