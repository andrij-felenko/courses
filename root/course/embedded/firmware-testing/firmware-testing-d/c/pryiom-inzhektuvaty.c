// БУЛО: годинник зашитий усередину — тест мусить чекати реальний час
bool timed_out_bad(uint32_t start) {
    return millis() - start > 5000;   // millis() — справжній лічильник
}

// СТАЛО: час подають ззовні — у бою справжній, у тесті керований
bool timed_out(uint32_t now, uint32_t start) {
    return now - start > 5000;
}

// тест — без жодного реального чекання, миттєво й детерміновано:
void test_timeout_boundary(void) {
    uint32_t t0 = 1000;
    TEST_ASSERT_FALSE( timed_out(t0 + 5000, t0) );  // рівно на межі — ще ні
    TEST_ASSERT_TRUE ( timed_out(t0 + 5001, t0) );  // на мілісекунду далі — так
}
