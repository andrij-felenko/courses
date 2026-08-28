void test_replay_guard(void) {
    replay_guard_t g;
    replay_guard_init(&g, 300); // толерантність 300 секунд

    time_t now = 1755723600;
    uint8_t nonce1[NONCE_LEN] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    uint8_t sig_valid[DIGEST_LEN] = {0xAA};
    uint8_t sig_invalid[DIGEST_LEN] = {0xBB};

    // Сценарій 1: Легітимний запит приймається
    assert(replay_guard_verify(&g, nonce1, now - 10, now, sig_valid, sig_valid) == AUTH_OK);

    // Сценарій 2: Повторний запит із тим самим Nonce відхиляється
    assert(replay_guard_verify(&g, nonce1, now - 5, now, sig_valid, sig_valid) == AUTH_REPLAY_DETECTED);

    // Сценарій 3: Застарілий запит (відхилення 400 секунд > 300 с)
    uint8_t nonce2[NONCE_LEN] = {2};
    assert(replay_guard_verify(&g, nonce2, now - 400, now, sig_valid, sig_valid) == AUTH_TIMESTAMP_SKEW);

    // Сценарій 4: Запит із майбутнього (годинник клієнта поспішає на 500 с)
    assert(replay_guard_verify(&g, nonce2, now + 500, now, sig_valid, sig_valid) == AUTH_TIMESTAMP_SKEW);

    // Сценарій 5: Некоректний підпис відхиляється
    assert(replay_guard_verify(&g, nonce2, now - 10, now, sig_valid, sig_invalid) == AUTH_INVALID_SIGNATURE);
}
