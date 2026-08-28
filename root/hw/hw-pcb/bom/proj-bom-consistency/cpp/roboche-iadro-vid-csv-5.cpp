struct BomRow {
    std::vector<std::string> refs;   // розгорнуті, нормалізовані позначення цього рядка
    int    qty;                      // заявлена кількість
    bool   has_mpn;                  // чи вказано номер деталі
    bool   dnp;                      // чи це «не монтувати»
    int    line_no;                  // номер рядка у файлі (для звіту)
};

// Чи містить поле примітки ознаку «не монтувати»?
static bool is_dnp(const std::string& note) {
    std::string n = note;
    for (char& c : n) if (c >= 'a' && c <= 'z') c -= 32;   // до верхнього регістру
    return n.find("DNP") != std::string::npos
        || n.find("DNI") != std::string::npos
        || n.find("DO NOT") != std::string::npos;
}

// Прочитати CSV переліку компонентів у вектор рядків.
// Колонки за порядком: 0 позначення, 1 кількість, 2 MPN, 3 примітка.
static std::vector<BomRow> read_bom(const std::string& path) {
    std::vector<BomRow> rows;
    FILE* fp = fopen(path.c_str(), "rb");
    if (!fp) { printf("не відкрити %s\n", path.c_str()); return rows; }

    char buf[4096];
    int line_no = 0;
    bool header_skipped = false;
    while (fgets(buf, sizeof(buf), fp)) {
        ++line_no;
        std::string line(buf);
        if (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (!line.empty() &&  line.back() == '\r') line.pop_back();   // CRLF
        if (line.empty()) continue;                                  // порожній рядок — пропуск
        if (!header_skipped) { header_skipped = true; continue; }    // шапка

        std::vector<std::string> f = split_csv_line(line);
        if (f.size() < 4) continue;                                  // надто короткий — ігнор

        BomRow row;
        row.refs    = parse_refdes_field(f[0]);
        row.qty     = atoi(trim(f[1]).c_str());
        row.has_mpn = !trim(f[2]).empty();
        row.dnp     = is_dnp(f[3]);
        row.line_no = line_no;
        rows.push_back(std::move(row));
    }
    fclose(fp);
    return rows;
}
