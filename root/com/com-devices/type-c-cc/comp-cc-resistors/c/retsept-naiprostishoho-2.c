cc_level_t lvl = usbc_read_profile();

uint16_t budget_ma;
switch (lvl) {
    case CC_3A0:     budget_ma = 3000; break;   // 15 Вт при 5 В
    case CC_1A5:     budget_ma = 1500; break;
    case CC_DEFAULT: budget_ma = 500;  break;   // консервативно: рівень USB2
    default:         budget_ma = 0;    break;    // нічого не під'єднано
}
set_input_current_limit(budget_ma);
