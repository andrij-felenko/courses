int32_t le32(const uint8_t *p) {          // у дроті молодший байт перший
    uint32_t u = uint32_t(p[0]) | uint32_t(p[1]) << 8 |
                 uint32_t(p[2]) << 16 | uint32_t(p[3]) << 24;
    return static_cast<int32_t>(u);
}

const FactMeta ALT_META{"висота", 0.001, 1};   // сире — цілі міліметри зі знаком

struct Vehicle {
    Vehicle(uint8_t id, Bus &bus) : sysid(id), altitude(ALT_META, bus) {}

    void handle(const Frame &f) {
        switch (f.msg) {
        case MSG_ALT:
            if (f.len >= 4) altitude.setRaw(le32(f.payload));  // мм лишаються мм
            break;
        case MSG_HEARTBEAT:
            if (f.len >= 1) armed = (f.payload[0] & 0x80) != 0;
            break;
        default: break;                    // решту потоку свідомо не чіпаємо
        }
    }
    uint8_t sysid;
    bool    armed = false;
    Fact    altitude;
};

class Router {
public:
    explicit Router(Bus &bus) : _bus(bus) {}

    Vehicle *route(const Frame &f) {
        if (f.sys == 0) return nullptr;                        // службова адреса
        for (auto &v : _vehicles) if (v->sysid == f.sys) return v.get();
        // новий апарат заводить лише серцебиття автопілота: камера теж б'є серцем
        if (f.msg != MSG_HEARTBEAT || f.comp != COMP_AUTOPILOT) return nullptr;
        _vehicles.push_back(std::make_unique<Vehicle>(f.sys, _bus));
        Vehicle &v = *_vehicles.back();
        if (onNewVehicle) onNewVehicle(v);
        return &v;
    }
    const std::vector<std::unique_ptr<Vehicle>> &vehicles() const { return _vehicles; }
    std::function<void(Vehicle &)> onNewVehicle;
private:
    Bus &_bus;
    // unique_ptr, а не Vehicle за значенням: посилання на апарат мусить пережити
    // зростання вектора, а всередині Fact ще й лежить лямбда з [this]
    std::vector<std::unique_ptr<Vehicle>> _vehicles;
};
