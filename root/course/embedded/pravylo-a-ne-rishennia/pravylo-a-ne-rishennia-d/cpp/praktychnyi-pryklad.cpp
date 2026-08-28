namespace {

void on_overheat(void*, int32_t) noexcept {
    // Пряме скидання регістрів ШІМ і активація кулера
}

void on_overpressure(void*, int32_t) noexcept {
    // Відкриття клапана скидання тиску
}

void on_estop(void*, int32_t) noexcept {
    // Повне знеструмлення силового контактора
}

constexpr std::array<RuleDef, 3> kSystemRules{{
    {
        .rule_id = 1,
        .fact_id = FactId::EstopPressed,
        .op = ConditionOp::Equals,
        .threshold_low = 1,
        .threshold_high = 1,
        .dwell_time_ms = 0,
        .interlock_mask = 0,
        .set_interlock = 0xFFFFFFFF,
        .action = on_estop,
        .action_param = 0
    },
    {
        .rule_id = 2,
        .fact_id = FactId::PressureKpa,
        .op = ConditionOp::GreaterThan,
        .threshold_low = 0,
        .threshold_high = 600,
        .dwell_time_ms = 50,
        .interlock_mask = 0x01,
        .set_interlock = 0x02,
        .action = on_overpressure,
        .action_param = 0
    },
    {
        .rule_id = 3,
        .fact_id = FactId::TempC,
        .op = ConditionOp::GreaterThan,
        .threshold_low = 0,
        .threshold_high = 95,
        .dwell_time_ms = 200,
        .interlock_mask = 0x03,
        .set_interlock = 0x04,
        .action = on_overheat,
        .action_param = 0
    }
}};

} // namespace
