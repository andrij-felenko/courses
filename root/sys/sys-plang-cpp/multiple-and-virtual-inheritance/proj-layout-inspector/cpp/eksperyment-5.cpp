struct ProbeBase {
    ProbeBase() {
        std::cout << "  [ProbeBase ctor] vptr points to ProbeBase vtable\n";
    }
    virtual void action() { std::cout << "  action -> ProbeBase\n"; }
    virtual ~ProbeBase() = default;
};

struct ProbeDerived : public ProbeBase {
    ProbeDerived() {
        std::cout << "  [ProbeDerived ctor] vptr updated to ProbeDerived vtable\n";
        action(); // Викликає ProbeDerived::action, а не нащадка
    }
    void action() override { std::cout << "  action -> ProbeDerived\n"; }
};

struct ProbeFinal : public ProbeDerived {
    ProbeFinal() {
        std::cout << "  [ProbeFinal ctor] vptr updated to ProbeFinal vtable\n";
    }
    void action() override { std::cout << "  action -> ProbeFinal\n"; }
};

void probe_construction_vtable_phases() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 5: Зміна vptr під час фаз конструювання\n";
    std::cout << "=========================================================\n";

    std::cout << "Створення екземпляра ProbeFinal:\n";
    ProbeFinal final_obj;
    std::cout << "Виклик action() після повного конструювання:\n";
    final_obj.action();
    std::cout << '\n';
}
