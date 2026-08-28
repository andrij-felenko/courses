/* Обчислення актуальності та семантичного статусу телеметрії (C) */
void evaluate_telemetry_staleness(uint32_t now_ms, uint32_t last_packet_ms, 
                                  SeverityLevel *sev, char *out_str, size_t max_len) {
    uint32_t age_ms = now_ms - last_packet_ms;

    if (age_ms >= 3000U) {
        *sev = SEV_CRITICAL;
        snprintf(out_str, max_len, "[X LOST: %.1fs]", (float)age_ms / 1000.0f);
    } else if (age_ms >= 1000U) {
        *sev = SEV_STALE;
        snprintf(out_str, max_len, "[⧗ STALE: %.1fs]", (float)age_ms / 1000.0f);
    } else {
        *sev = SEV_NORMAL;
        snprintf(out_str, max_len, "[OK ONLINE]");
    }
}
