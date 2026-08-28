class Guest {
public:
    template <class S>
        requires (!std::is_base_of_v<Guest, std::remove_cvref_t<S>>)
              && std::constructible_from<std::string, S>
    explicit Guest(S&& src) : name_(std::forward<S>(src)) { say("шаблонний конструктор"); }

    Guest(const Guest& other) : name_(other.name_) { say("конструктор копіювання"); }
    Guest(Guest&& other) noexcept : name_(std::move(other.name_)) { say("конструктор переміщення"); }

    const std::string& name() const { return name_; }

private:
    static void say(const char* what) { std::printf("      %s\n", what); }
    std::string name_;
};

struct Vip : Guest {
    Vip() : Guest("вельможа") {}
};
