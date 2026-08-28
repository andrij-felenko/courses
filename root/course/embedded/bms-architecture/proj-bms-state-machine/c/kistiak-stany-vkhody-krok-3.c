// Єдині двері у відмову. Порядок усередині — НЕ випадковий.
static void enter_fault(fault_code_t code)
{
    // 1) Найперше — РОЗІРВАТИ коло. Дії над контакторами раніше за все інше.
    contactor_main(false);
    contactor_pre(false);
    contactor_neg(false);

    // 2) Зафіксувати ПЕРШУ причину; повторні виклики її не затирають.
    if (bms.fault == FAULT_NONE) bms.fault = code;

    bms.state = BMS_FAULT;
    set_fault_pin(true);          // підняти апаратний прапор відмови
}
