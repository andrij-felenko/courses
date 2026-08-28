// Розібрати поле позначень рядка BOM ("R1-R4, R7") у список окремих нормалізованих
// позначень: ["R1","R2","R3","R4","R7"]. Спершу ділимо за комами, тоді кожен
// шматок розгортаємо як можливий діапазон.
static std::vector<std::string> parse_refdes_field(const std::string& field) {
    std::vector<std::string> refs;
    std::string tok;
    // поле вже без зовнішніх лапок (їх зняв split_csv_line), тож ділимо просто за комами
    for (size_t i = 0; i <= field.size(); ++i) {
        if (i == field.size() || field[i] == ',') {
            std::string t = trim(tok);
            if (!t.empty())
                for (auto& r : expand_range(t)) refs.push_back(r);
            tok.clear();
        } else {
            tok.push_back(field[i]);
        }
    }
    return refs;
}
