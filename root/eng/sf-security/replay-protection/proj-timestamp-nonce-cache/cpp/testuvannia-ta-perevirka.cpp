void test_replay_guard_cpp() {
    ReplayGuard<1024> g(std::chrono::seconds(300));

    const auto now = std::chrono::system_clock::from_time_t(1755723600);
    ReplayGuard<1024>::Nonce nonce1{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    ReplayGuard<1024>::Nonce nonce2{2};

    ReplayGuard<1024>::Digest sig_valid{};
    sig_valid.fill(0xAA);
    ReplayGuard<1024>::Digest sig_invalid{};
    sig_invalid.fill(0xBB);

    // Сценарій 1: Легітимний запит приймається
    assert(g.verify_and_record(nonce1, now - std::chrono::seconds(10), now, sig_valid, sig_valid) == AuthResult::Ok);

    // Сценарій 2: Повтор того самого Nonce відхиляється
    assert(g.verify_and_record(nonce1, now - std::chrono::seconds(5), now, sig_valid, sig_valid) == AuthResult::ReplayDetected);

    // Сценарій 3: Застарілий запит
    assert(g.verify_and_record(nonce2, now - std::chrono::seconds(400), now, sig_valid, sig_valid) == AuthResult::TimestampSkew);

    // Сценарій 4: Запит із далекого майбутнього
    assert(g.verify_and_record(nonce2, now + std::chrono::seconds(500), now, sig_valid, sig_valid) == AuthResult::TimestampSkew);

    // Сценарій 5: Невалідний підпис
    assert(g.verify_and_record(nonce2, now - std::chrono::seconds(10), now, sig_valid, sig_invalid) == AuthResult::InvalidSignature);
}
