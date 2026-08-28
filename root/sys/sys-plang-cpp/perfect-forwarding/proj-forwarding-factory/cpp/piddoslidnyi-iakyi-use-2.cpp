class Probe {
public:
    explicit Probe(std::string name) : name_(std::move(name)) {
        ++tally.made;
        note("конструктор");
    }
    Probe(const Probe& other) : name_(other.name_), hollow_(other.hollow_) {
        ++tally.copied;
        note("КОПІЮВАННЯ");
    }
    Probe(Probe&& other) noexcept
        : name_(std::move(other.name_)), hollow_(other.hollow_) {
        other.hollow_ = true;                    // джерело віддало вміст
        ++tally.moved;
        note("переміщення");
    }
    Probe& operator=(const Probe&) = delete;
    Probe& operator=(Probe&&) = delete;

    const char* text() const { return hollow_ ? "<порожньо>" : name_.c_str(); }

private:
    void note(const char* what) const {
        if (verbose) std::printf("      %s%s\n", pad(what, 14).c_str(), text());
    }
    std::string name_;
    bool hollow_ = false;
};
