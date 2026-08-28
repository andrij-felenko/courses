void run_replay_tests_cpp() {
    ReplayWindow<2> w;

    // 1. Нульовий номер відхиляється
    assert(w.check(0) == ReplayStatus::TooOld);

    // 2. Перший пакет
    assert(w.check(1) == ReplayStatus::Ok);
    w.commit(1);
    assert(w.max_sequence() == 1);

    // 3. Дублікат першого пакета
    assert(w.check(1) == ReplayStatus::Duplicate);

    // 4. Стрибок уперед на 100
    assert(w.check(100) == ReplayStatus::Ok);
    w.commit(100);
    assert(w.max_sequence() == 100);

    // 5. Запізнілий пакет у межах вікна (100 - 95 = 5 < 128)
    assert(w.check(95) == ReplayStatus::Ok);
    w.commit(95);
    assert(w.check(95) == ReplayStatus::Duplicate);

    // 6. Застарілий пакет після зсуву вікна
    w.commit(300);
    assert(w.check(95) == ReplayStatus::TooOld);
}
