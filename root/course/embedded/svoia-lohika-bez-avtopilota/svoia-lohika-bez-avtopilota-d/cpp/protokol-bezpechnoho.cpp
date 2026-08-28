void GoalEngine::abort_all() noexcept {
    // 1. Безпечне завершення та очищення активної цілі
    if (active_goal_) {
        if (active_goal_->on_abort_cleanup != nullptr) {
            active_goal_->on_abort_cleanup(context_);
        }
        active_goal_.reset();
    }

    // 2. Очищення черги майбутніх кроків
    while (!queue_.empty()) {
        queue_.pop();
    }
}
