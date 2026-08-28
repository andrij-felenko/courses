void run_replay_tests(void) {
    replay_window_t w;
    replay_window_init(&w);

    // 1. Нульовий номер відхиляється
    assert(replay_window_check(&w, 0) == REPLAY_TOO_OLD);

    // 2. Перший пакет
    assert(replay_window_check(&w, 1) == REPLAY_OK);
    replay_window_commit(&w, 1);
    assert(w.seq_max == 1);

    // 3. Дублікат першого пакета
    assert(replay_window_check(&w, 1) == REPLAY_DUPLICATE);

    // 4. Стрибок уперед на 100
    assert(replay_window_check(&w, 100) == REPLAY_OK);
    replay_window_commit(&w, 100);
    assert(w.seq_max == 100);

    // 5. Запізнілий пакет у межах вікна (100 - 95 = 5 < 128)
    assert(replay_window_check(&w, 95) == REPLAY_OK);
    replay_window_commit(&w, 95);
    assert(replay_window_check(&w, 95) == REPLAY_DUPLICATE);

    // 6. Занадто старий пакет (100 - 1 = 99 < 128, але якщо seq_max зросте до 300)
    replay_window_commit(&w, 300);
    assert(replay_window_check(&w, 95) == REPLAY_TOO_OLD);
}
