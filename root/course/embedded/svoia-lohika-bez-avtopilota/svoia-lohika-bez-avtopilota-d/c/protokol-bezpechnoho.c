void goal_engine_abort_all(GoalEngine *ge) {
    /* 1. Викликати специфічний деструктор активної цілі */
    if (ge->has_active_goal && ge->active_goal.on_abort_cleanup != NULL) {
        ge->active_goal.on_abort_cleanup(ge->context);
    }

    /* 2. Атомарно очистити кільцевий буфер майбутніх завдань */
    ge->head = 0;
    ge->tail = 0;
    ge->count = 0;
    ge->has_active_goal = false;
    memset(&ge->active_goal, 0, sizeof(Goal));
}
