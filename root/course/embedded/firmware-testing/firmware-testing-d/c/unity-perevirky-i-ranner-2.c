static Thermostat t;
void setUp(void)    { thermostat_init(&t); }   // перед КОЖНИМ тестом
void tearDown(void) { /* нічого звільняти */ }

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_overheat_triggers_safe_mode);
    RUN_TEST(test_normal_temp_keeps_running);
    return UNITY_END();   // ненульовий код = були провали (для CI)
}
