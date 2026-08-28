// Викликати ОДИН раз при старті прошивки, ДО першого bms_step().
void bms_init(void)
{
    // 1) Найперше — фізично знеструмити всі котушки. Не покладаємось на
    //    те, в якому стані GPIO лишив попередній (можливо, аварійний) сеанс.
    contactor_main(false);
    contactor_pre(false);
    contactor_neg(false);
    set_fault_pin(false);

    // 2) Чистий безпечний стан. Після збою живлення НЕ «відновлюємо» ON —
    //    збираємо коло заново через передзаряд.
    bms = (bms_t){ .state = BMS_OFF, .fault = FAULT_NONE };
    main_cmd = false;

    // 3) Якщо в незалежній пам'яті лишився слід попередньої відмови —
    //    стартуємо одразу у FAULT, а не вдаємо, що нічого не було.
    fault_code_t persisted = nvm_read_last_fault();
    if (persisted != FAULT_NONE) {
        bms.fault = persisted;
        bms.state = BMS_FAULT;
        set_fault_pin(true);
    }
}
