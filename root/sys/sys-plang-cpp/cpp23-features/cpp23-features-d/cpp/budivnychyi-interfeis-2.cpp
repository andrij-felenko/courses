struct BaseBuilder {
    template <typename Self>
    Self&& set_tag(this Self&& self, std::string_view t) {
        self.tag = t;
        return std::forward<Self>(self);
    }
    std::string tag;
};

struct HttpBuilder : BaseBuilder {
    template <typename Self>
    Self&& set_port(this Self&& self, int p) {
        self.port = p;
        return std::forward<Self>(self);
    }
    int port{80};
};

// Працює ідеально в C++23:
auto req = HttpBuilder{}.set_tag("api").set_port(8080);
