// Єдині двері в ABORT: лишаємо старе калібрування недоторканим.
static void cal_abort(cal_err_t why)
{
    cal.err   = why;
    cal.state = CAL_ABORT;       // нічого НЕ пишемо в NVS — старе чинне лишається
    ui_prompt("Калібрування скасовано");
}

// Почати усереднення на черговій опорі: обнулити накопичувач.
static void avg_begin(uint32_t t)
{
    cal.acc = 0; cal.n = 0;
    cal.raw_min = INT32_MAX; cal.raw_max = INT32_MIN;
    cal.t_enter = t;
}
