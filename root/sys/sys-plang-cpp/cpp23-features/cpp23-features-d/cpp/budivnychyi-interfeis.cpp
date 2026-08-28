// Проблема у C++20: зрізання типу при успадкуванні
struct BaseBuilder {
    BaseBuilder& set_tag(std::string_view t) { tag = t; return *this; }
    std::string tag;
};

struct HttpBuilder : BaseBuilder {
    HttpBuilder& set_port(int p) { port = p; return *this; }
    int port{80};
};

// HttpBuilder().set_tag("api").set_port(8080); // Помилка компіляції: set_tag повертає BaseBuilder&
