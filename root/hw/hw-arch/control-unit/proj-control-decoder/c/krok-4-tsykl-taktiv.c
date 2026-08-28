static const char *stage_name(Stage s) {
    static const char *n[] = {"FETCH","DECODE","ADDR","READ",
                              "CALC","WRITE_REG","WRITE_MEM","DONE"};
    return n[s];
}

// Прогнати одну команду до кінця, друкуючи, що робиться кожного такту.
void run_one_instruction(ControlUnit *cu, Datapath *dp) {
    int tick = 0;
    do {
        mem_tick(dp);                   // пам'ять просувається
        Stage before = cu->stage;
        Control c = cu_step(cu, dp);    // крок автомата
        printf("такт %2d | стадія %-9s | rd=%d wr=%d alu=%d regW=%d ready=%d\n",
               tick++, stage_name(before),
               c.mem_read, c.mem_write, c.alu_enable, c.reg_write, dp->mem_ready);
    } while (cu->stage != S_FETCH);     // поки команда не завершилась
}
