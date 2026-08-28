/* Процедурне використання у стилі чистого C */
return_budget_handle_t g_budget_handle;
return_config_t g_budget_cfg = { ... };

void flight_init(void) {
    int32_t rc = return_budget_init(&g_budget_handle, &g_budget_cfg);
    if (rc != RETURN_OK) {
        panic_halt("Budget init failed");
    }
}
