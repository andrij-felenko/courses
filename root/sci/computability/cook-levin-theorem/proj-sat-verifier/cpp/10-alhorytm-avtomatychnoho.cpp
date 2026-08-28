void add_tseytin_clause(std::vector<std::string>& clauses, std::span<const int> literals, int& next_var_id) {
    if (literals.size() <= 3) {
        std::string cl;
        for (int lit : literals) cl += std::to_string(lit) + " ";
        clauses.push_back(cl + "0");
        return;
    }
    int z_prev = next_var_id++;
    clauses.push_back(std::format("{} {} {} 0", literals[0], literals[1], z_prev));
    for (size_t i = 2; i < literals.size() - 2; ++i) {
        int z_next = next_var_id++;
        clauses.push_back(std::format("-{} {} {} 0", z_prev, literals[i], z_next));
        z_prev = z_next;
    }
    clauses.push_back(std::format("-{} {} {} 0", z_prev, literals[literals.size()-2], literals.back()));
}
