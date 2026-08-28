void IntervalNode::update_max() noexcept {
    double cur_max = interval.high;
    if (left) {
        cur_max = std::max(cur_max, left->max_high);
    }
    if (right) {
        cur_max = std::max(cur_max, right->max_high);
    }
    max_high = cur_max;
}
