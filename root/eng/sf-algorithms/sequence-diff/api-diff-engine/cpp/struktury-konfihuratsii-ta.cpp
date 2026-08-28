namespace diff {

struct Config {
    Algorithm algorithm{Algorithm::Myers};
    size_t context_lines{3};
    bool ignore_whitespace_eol{false};
    bool ignore_all_whitespace{false};
    size_t max_edit_distance{0}; // 0 = без обмежень
};

struct LineEntry {
    Operation op{Operation::Keep};
    size_t old_line_num{0};
    size_t new_line_num{0};
    std::string_view text;
};

struct Hunk {
    size_t old_start{0};
    size_t old_count{0};
    size_t new_start{0};
    size_t new_count{0};
    std::vector<LineEntry> entries;
};

struct Result {
    std::vector<Hunk> hunks;
    size_t total_deletions{0};
    size_t total_insertions{0};
    size_t edit_distance{0};
};

} // namespace diff
