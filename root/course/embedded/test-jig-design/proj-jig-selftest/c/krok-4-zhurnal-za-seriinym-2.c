void jig_run_one_board(void) {
    jig_power_on_dut();          // подати живлення на плату (з контролем струму!)

    char line[LINE_MAX];
    if (!jig_read_line(line, sizeof(line), REPORT_TIMEOUT_MS)) {
        // рапорту нема — окремий, найпідступніший випадок (див. пастки)
        jig_show(RED, "NO REPLY");
        jig_log(jig_last_known_serial(), &(verdict_t){ .passed = false,
                                                       .reason = "no reply / timeout" });
        jig_power_off_dut();
        return;
    }

    // серійник дістаємо ДО суду — він потрібен і для журналу, і якщо суд завалиться
    char serial[16] = "UNKNOWN";
    field_str(line, "SN", serial, sizeof(serial));

    verdict_t v = jig_judge(line);
    jig_log(serial, &v);
    jig_show(v.passed ? GREEN : RED, v.passed ? "PASS" : v.reason);

    jig_power_off_dut();         // зняти живлення, плата готова до заміни
}
