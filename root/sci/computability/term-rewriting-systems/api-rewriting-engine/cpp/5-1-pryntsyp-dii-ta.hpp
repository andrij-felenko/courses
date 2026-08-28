namespace trs {

class DiscriminationTree {
public:
    DiscriminationTree();
    ~DiscriminationTree();

    // Додавання правила в індексний префіксний граф
    void insert_rule(const RewriteRule& rule);

    // Видалення правила з індексу
    void remove_rule(uint32_t rule_id);

    // Пошук усіх правил, чия ліва частина зіставляється з термом target
    std::vector<RewriteRule> find_applicable_rules(TermPtr target) const;

    // Пошук усіх термів в індексі, які уніфікуються з виразом query
    std::vector<RewriteRule> find_unifiable_rules(TermPtr query) const;

    // Очищення структури
    void clear();
};

} // namespace trs
