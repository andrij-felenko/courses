typedef struct {
    uint32_t  serial;     // серійний номер виробу
    uint32_t  t_unix;     // мітка часу
    verdict_t verdict;    // V_PASS / V_FAIL
    uint16_t  v_test;     // напруга проби, В
    uint16_t  i_leak_ua;  // виміряний виток, мкА
    char      reason[24]; // причина провалу (або "")
} record_t;

void log_result(const hipot_t *h) {
    record_t r = {0};
    r.serial    = current_serial();
    r.t_unix    = rtc_now();
    r.verdict   = h->verdict;
    r.v_test    = code_to_volts(h->dac_target);
    r.i_leak_ua = leak_microamps();
    if (h->verdict == V_FAIL && h->fail_reason)
        strncpy(r.reason, h->fail_reason, sizeof r.reason - 1);
    fram_append(&r, sizeof r);   // тільки дозапис, у FRAM/SD
}
