class JsonReport : public Report {
public:
    std::string render(const std::vector<Field>& fields) const override {
        std::string s = "{";
        for (std::size_t i = 0; i < fields.size(); ++i) {
            if (i) s += ",";
            s += "\"" + fields[i].key + "\":\"" + fields[i].value + "\"";
        }
        return s + "}";           // ← і голова, і хвіст зникли, і ніхто не сказав
    }
};
