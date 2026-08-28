// Розгорнути BusName у список імен членів.
// "D[7..0]" → {"D7","D6",...,"D0"};  "D[0..7]" → {"D0","D1",...,"D7"}.
// Скаляр "CLK" → {"CLK"} (один член — він сам).
static std::vector<std::string> expand(const BusName& bn) {
    std::vector<std::string> members;
    if (!bn.is_vector) {
        members.push_back(bn.prefix);        // скаляр — сам собі єдиний член
        return members;
    }
    int step = (bn.left <= bn.right) ? +1 : -1;   // напрям перелічення
    for (int i = bn.left; ; i += step) {
        members.push_back(bn.prefix + std::to_string(i));   // "D" + "7" = "D7"
        if (i == bn.right) break;            // дійшли до другого кінця — стоп
    }
    return members;
}
