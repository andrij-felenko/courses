class Validator {
    // ворота — невіртуальні, як завжди
public:
    void check(const Request& r) const {
        if (r.id == 0) throw std::invalid_argument("check: нема id");  // спільна передумова
        rules(r);                                                       // ← дірка-надбудова
    }
    virtual ~Validator() = default;
protected:
    // protected — саме тому, що нащадок МУСИТЬ надбудувати цю базову перевірку
    virtual void rules(const Request& r) const {
        if (r.size == 0) throw std::invalid_argument("rules: порожній запит");
    }
};

class StrictValidator : public Validator {
protected:
    void rules(const Request& r) const override {
        Validator::rules(r);                       // спершу базові правила — тепер це можна
        if (r.size > MAX) throw std::invalid_argument("rules: завеликий запит");
    }
    static constexpr std::size_t MAX = 4096;
};
