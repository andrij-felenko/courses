// C: порядок — перевірка під час ВИКОНАННЯ.
// Помилку («гіпот без опору ізоляції») ловимо на стенді, не в компіляторі.
static void go_hipot(hipot_t *h) {
    if (h->state != ST_INSUL_RES || h->verdict == V_FAIL) {
        abort_test(h, "гіпот без пройденого опору ізоляції");
        return;
    }
    ramp_setup(h, volts_to_code(2121), 2000);
    g_arc_armed = true;
    enter(h, ST_HIPOT_RAMP);
}
