class Report {
public:
    // публічний ВІРТУАЛЬНИЙ метод: нащадок його перевизначить
    virtual std::string render(const std::vector<Field>& fields) const {
        std::string out = header(fields.size());   // спільна голова
        for (const auto& f : fields)               // типове тіло
            out += f.key + ": " + f.value + "\n";
        out += footer();                            // спільний хвіст
        return out;
    }
    virtual ~Report() = default;
protected:
    std::string header(std::size_t n) const { return "=== REPORT (" + std::to_string(n) + ") ===\n"; }
    std::string footer() const { return "=== END ===\n"; }
};
