// знімається із ЗАПИТУ в мить збереження, за переліком із Vary у ВІДПОВІДІ
std::vector<std::pair<std::string, std::string>>
selecting_values(const Fields& response, const Fields& request) {
    std::vector<std::pair<std::string, std::string>> out;
    for (std::string name : split_list(value_of(response, "vary"))) {
        lower_inplace(name);
        const std::string* v = request.find(name);
        // відсутність заголовка — теж значення, і воно має збігатися з відсутністю
        out.emplace_back(name, v ? normalize(name, *v) : std::string());
    }
    return out;
}

bool variant_matches(const Entry& e, const Fields& request) {
    for (const auto& [name, stored] : e.selecting) {
        const std::string* now = request.find(name);
        const std::string  cur = now ? normalize(name, *now) : std::string();
        if (cur != stored) return false;
    }
    return true;
}
