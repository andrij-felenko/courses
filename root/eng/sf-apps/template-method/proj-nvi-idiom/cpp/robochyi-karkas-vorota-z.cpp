class TextReport : public Report {
    // без специфікатора → private за замовчуванням; так і має бути
    std::string renderBody(const std::vector<Field>& fields) const override {
        std::string s;
        for (const auto& f : fields)
            s += f.key + ": " + f.value + "\n";
        s.pop_back();               // прибрати останній перенос — цього вимагає післяумова
        return s;
    }
};

class JsonReport : public Report {
    std::string renderBody(const std::vector<Field>& fields) const override {
        std::string s = "{";
        for (std::size_t i = 0; i < fields.size(); ++i) {
            if (i) s += ",";
            s += "\"" + fields[i].key + "\":\"" + fields[i].value + "\"";
        }
        return s + "}";
    }
};
