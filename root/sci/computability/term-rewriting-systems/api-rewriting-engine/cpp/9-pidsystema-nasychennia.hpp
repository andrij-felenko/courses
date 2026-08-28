namespace trs {

using EClassId = uint32_t;

class EGraph {
public:
    EGraph();
    ~EGraph();

    // Додавання терма до графа конгруентності (повертає ідентифікатор класу еквівалентності)
    EClassId add_term(TermPtr term);

    // Злиття двох класів еквівалентності на основі доведеної рівності
    void merge_classes(EClassId id1, EClassId id2);

    // Відновлення інваріантів конгруентності після пачки злить
    void rebuild_congruence();

    // Виконання одного раунду насичення рівностями за правилами rewrite_rules
    size_t saturate_step(const std::vector<RewriteRule>& rules);

    // Екстракція оптимального терма з класу еквівалентності за функцією вартості
    TermPtr extract_best(EClassId id, const std::function<double(TermPtr)>& cost_fn) const;
};

} // namespace trs
