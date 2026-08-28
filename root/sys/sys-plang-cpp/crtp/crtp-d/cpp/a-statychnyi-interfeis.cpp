template <typename Derived>
class DataParser {
public:
    // Головний шаблонний алгоритм
    void parse_pack() {
        auto& self = *static_cast<Derived*>(this);
        self.read_header();
        self.read_body();
        self.verify_checksum();
    }
};

class JsonParser : public DataParser<JsonParser> {
public:
    void read_header() { /* Читання JSON заголовка */ }
    void read_body() { /* Розбір JSON тіла */ }
    void verify_checksum() { /* Перевірка суми */ }
};
