// Прочитати простий список позначень (одне на рядок) у мапу «позначення → скільки
// разів трапилось». Саме МАПА лічильників, а не множина: множина мовчки злила б
// два однакові написи R7 на платі (дублікат майданчика — помилка розведення) в один
// елемент і сховала б реальну проблему. Рахуючи появи, ми зможемо її зловити пізніше —
// так само, як на боці BOM. До множини зведемо потім, після підрахунку дублікатів.
static std::unordered_map<std::string,int> read_ref_counts(const std::string& path) {
    std::unordered_map<std::string,int> counts;
    FILE* fp = fopen(path.c_str(), "rb");
    if (!fp) { printf("не відкрити %s\n", path.c_str()); return counts; }
    char buf[256];
    while (fgets(buf, sizeof(buf), fp)) {
        std::string r = norm_ref(buf);
        if (!r.empty()) ++counts[r];      // побачили ще раз — лічильник росте
    }
    fclose(fp);
    return counts;
}
