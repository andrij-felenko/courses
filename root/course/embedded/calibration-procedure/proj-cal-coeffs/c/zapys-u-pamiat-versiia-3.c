static void save_step(uint32_t t)
{
    (void)t;
    if (cal_store_write(&cal.result)) {
        cal.state = CAL_DONE;
        ui_prompt("Калібрування збережено");
    } else {
        cal_abort(CAL_ERR_STORE);          // носій не підтвердив запис
    }
}
