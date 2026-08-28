void validate_invariants(const geo::IntervalNode* node) {
    if (!node) return;

    // 1. Перевірка лівого сина
    if (node->left) {
        assert(node->left->interval.low <= node->interval.low && "Порушення порядку BST у лівому синові");
        validate_invariants(node->left.get());
    }

    // 2. Перевірка правого сина
    if (node->right) {
        assert(node->right->interval.low >= node->interval.low && "Порушення порядку BST у правому синові");
        validate_invariants(node->right.get());
    }

    // 3. Точна перевірка max_high
    double expected_max = node->interval.high;
    if (node->left) expected_max = std::max(expected_max, node->left->max_high);
    if (node->right) expected_max = std::max(expected_max, node->right->max_high);

    assert(node->max_high == expected_max && "Порушення інваріанта max_high!");
}
