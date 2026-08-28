// 1. Скалярна структура без спеціальних методів
struct SensorHeader {
    uint32_t device_id;
    uint16_t packet_seq;
};

// 2. Клас користувача з власним методом
struct UserProfile {
    uint64_t uid;
    std::string name;

    void serialize(Buffer& buf) const {
        const uint8_t* id_p = reinterpret_cast<const uint8_t*>(&uid);
        buf.insert(buf.end(), id_p, id_p + sizeof(uid));
        uint32_t len = static_cast<uint32_t>(name.size());
        const uint8_t* len_p = reinterpret_cast<const uint8_t*>(&len);
        buf.insert(buf.end(), len_p, len_p + sizeof(len));
        buf.insert(buf.end(), name.begin(), name.end());
    }
};

// 3. Сторонній тип із вільною функцією у власному просторі імен
namespace external_geo {
    struct Coordinates {
        double latitude;
        double longitude;
    };

    void serialize(Buffer& buf, const Coordinates& c) {
        const uint8_t* p = reinterpret_cast<const uint8_t*>(&c);
        buf.insert(buf.end(), p, p + sizeof(c));
    }
}

int main() {
    Buffer stream;

    // Тест 1: Сирі байти
    SensorHeader hdr{101, 42};
    write_data(stream, hdr);

    // Тест 2: Метод-член
    UserProfile profile{99999, "system_admin"};
    write_data(stream, profile);

    // Тест 3: Вільна функція через ADL
    external_geo::Coordinates geo{50.4501, 30.5234};
    write_data(stream, geo);

    // Тест 4: Контейнер
    std::vector<int> numbers = {100, 200, 300};
    write_data(stream, numbers);

    std::cout << "Успішно записано " << stream.size() << " байтів.\n";
    return 0;
}
