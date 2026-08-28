// Надрукувати позначення з a, яких немає в b, під заданим кодом і підписом.
static int report_diff(const std::unordered_set<std::string>& a,
                       const std::unordered_set<std::string>& b,
                       int code, const char* msg)
{
    // зробимо вивід упорядкованим, щоб звіт був стабільний між запусками
    std::vector<std::string> missing;
    for (const auto& x : a) if (!b.count(x)) missing.push_back(x);
    std::sort(missing.begin(), missing.end());
    for (const auto& x : missing)
        printf("[E%d] %s: %s\n", code, msg, x.c_str());
    return (int)missing.size();
}

// Надрукувати позначення, що трапилися в списку БІЛЬШЕ одного разу — дублікат на платі
// чи у схемі, який множина сховала б. Мапа лічильників це якраз показує.
static int report_dups(const std::unordered_map<std::string,int>& counts,
                       const char* source)
{
    std::vector<std::string> dups;
    for (const auto& kv : counts) if (kv.second > 1) dups.push_back(kv.first);
    std::sort(dups.begin(), dups.end());
    for (const auto& x : dups)
        printf("[E%d] позначення %s трапляється %s більше одного разу\n",
               ERR_DUP_REFDES, x.c_str(), source);
    return (int)dups.size();
}

// Звести мапу лічильників до звичайної множини позначень — для різниць.
static std::unordered_set<std::string> keys_of(
        const std::unordered_map<std::string,int>& counts)
{
    std::unordered_set<std::string> s;
    for (const auto& kv : counts) s.insert(kv.first);
    return s;
}

// Повна перевірка: повертає 0, якщо все чисто, або кількість проблем.
static int check_consistency(const std::vector<BomRow>& bom_rows,
                             const std::unordered_map<std::string,int>& schem_counts,
                             const std::unordered_map<std::string,int>& board_counts)
{
    int problems = 0;

    // 1) внутрішні перевірки BOM + збір мапи «позначення → рядок» (ловить дублікати BOM)
    std::unordered_map<std::string,int> bom_map;          // позначення → рядок
    problems += check_bom_internal(bom_rows, bom_map);

    // 2) дублікати НА ПЛАТІ та У СХЕМІ — те, що множина сама сховала б
    problems += report_dups(board_counts, "на платі");
    problems += report_dups(schem_counts, "у схемі");

    // 3) зводимо кожне джерело до множини позначень
    std::unordered_set<std::string> bom;                  // множина позначень BOM
    for (const auto& kv : bom_map) bom.insert(kv.first);
    std::unordered_set<std::string> schem = keys_of(schem_counts);
    std::unordered_set<std::string> board = keys_of(board_counts);

    // 4) різниці множин — кожна під своїм кодом
    problems += report_diff(board, bom,   ERR_ORPHAN_BOARD,  "є на платі, нема в BOM");
    problems += report_diff(bom,   board, ERR_ORPHAN_BOM,    "є в BOM, нема на платі");
    problems += report_diff(bom,   schem, ERR_BOM_NOT_SCHEM, "є в BOM, нема в схемі");
    problems += report_diff(schem, board, ERR_SCHEM_NOT_BRD, "є в схемі, нема на платі");

    return problems;
}
