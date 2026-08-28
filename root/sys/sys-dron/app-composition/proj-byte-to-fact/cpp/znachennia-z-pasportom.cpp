struct Unit { const char *name; double perBase; };  // скільки базових одиниць в одній показаній

struct FactMeta {
    const char *name;       // назва для людини
    double      rawToBase;  // «сирі одиниці → базові»: мм → м це 0.001
    int         decimals;   // скільки знаків показувати
};

class Fact {
public:
    Fact(const FactMeta &m, Bus &bus) : _m(m), _bus(bus) {}

    void setRaw(int32_t raw) {           // рівно те, що приїхало в кадрі
        ++calls;
        if (raw == _raw) return;         // те саме число — новини немає
        _raw = raw;
        ++changes;
        _bus.post(this, [this] { if (onChanged) onChanged(*this); });
    }

    int32_t raw() const { return _raw; }
    double cooked(const Unit &u) const { return _raw * _m.rawToBase / u.perBase; }

    std::string display(const Unit &u) const {
        char buf[64];
        std::snprintf(buf, sizeof buf, "%.*f %s", _m.decimals, cooked(u), u.name);
        return buf;
    }
    const char *name() const { return _m.name; }

    std::function<void(Fact &)> onChanged;
    uint32_t calls = 0, changes = 0;     // лічильники лише для демонстрації
private:
    const FactMeta &_m;
    Bus            &_bus;
    int32_t         _raw = 0;
};
