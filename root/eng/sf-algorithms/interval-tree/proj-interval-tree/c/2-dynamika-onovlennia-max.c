void update_node_max(IntervalNode* node) {
    if (!node) return;
    double current_max = node->interval.high;
    if (node->left && node->left->max_high > current_max) {
        current_max = node->left->max_high;
    }
    if (node->right && node->right->max_high > current_max) {
        current_max = node->right->max_high;
    }
    node->max_high = current_max;
}
