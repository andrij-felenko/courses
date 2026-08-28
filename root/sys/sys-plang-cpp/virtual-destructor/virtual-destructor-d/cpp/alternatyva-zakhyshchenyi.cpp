class NonDeletableMixin {
protected:
    ~NonDeletableMixin() = default; // Не віртуальний, але захищений!

public:
    void utility_helper() { /* спільний функціонал */ }
};

class ConcreteWorker : public NonDeletableMixin {
public:
    ~ConcreteWorker() = default; // Публічний деструктор нащадка
};
