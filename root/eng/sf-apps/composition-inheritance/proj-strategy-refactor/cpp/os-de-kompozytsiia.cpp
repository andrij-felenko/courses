// Нова вісь — новий інтерфейс + по одному класу на вид. І ВСЕ.
struct Element {
    virtual int  bonus() const = 0;     // додаткова шкода від стихії
    virtual const char* name() const = 0;
    virtual ~Element() = default;
};
struct Plain : Element {
    int bonus() const override { return 0; }
    const char* name() const override { return "звичайна"; }
};
struct Fire : Element {
    int bonus() const override { return 4; }
    const char* name() const override { return "вогонь"; }
};
struct Ice : Element {
    int bonus() const override { return 3; }
    const char* name() const override { return "крига"; }
};
