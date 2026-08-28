// Перевірити кожен рядок BOM окремо + зібрати мапу «позначення → номер рядка»,
// дорогою ловлячи дублікати. Повертає кількість знайдених проблем.
static int check_bom_internal(const std::vector<BomRow>& rows,
                              std::unordered_map<std::string,int>& ref_to_line)
{
    int problems = 0;
    for (const auto& r : rows) {
        // (1) Кількість мусить дорівнювати довжині переліку позначень.
        if (r.qty != (int)r.refs.size()) {
            printf("[E%d] рядок %d: К-сть=%d, а позначень перелічено %zu\n",
                   ERR_QTY_MISMATCH, r.line_no, r.qty, r.refs.size());
            ++problems;
        }
        // (2) Монтуємо без MPN — нічого замовити. DNP без MPN — НОРМА, не чіпаємо.
        if (!r.dnp && !r.has_mpn) {
            printf("[E%d] рядок %d: монтований рядок без MPN — закупити нічим\n",
                   ERR_NO_MPN, r.line_no);
            ++problems;
        }
        // (3) Дублікати позначень: те саме позначення вже зустрічалось.
        for (const auto& ref : r.refs) {
            auto it = ref_to_line.find(ref);
            if (it != ref_to_line.end()) {
                printf("[E%d] позначення %s повторюється: рядки %d і %d\n",
                       ERR_DUP_REFDES, ref.c_str(), it->second, r.line_no);
                ++problems;
            } else {
                ref_to_line.emplace(ref, r.line_no);
            }
        }
    }
    return problems;
}
