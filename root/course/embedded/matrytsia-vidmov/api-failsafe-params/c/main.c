/* Стендовий прогін підсистеми: старт із чистого сектора, збереження
 * конфігурації, псування комірки Flash, передпольотна валідація
 * і сценарій "обрив керування під час глушіння GNSS". */

#include "fs_params.h"
#include "fs_status.h"
#include "fs_storage.h"

#include <stdio.h>
#include <string.h>

#define RTL_ALT_M 60.0f

static void cli_status(const fs_param_block_t *p, const failsafe_telemetry_t *t)
{
    printf("[failsafe] Active faults mask : 0x%08lX (%s)\n",
           (unsigned long)t->active_faults_mask,
           t->active_faults_mask == 0u ? "CLEAN" : "FAULT");
    for (int i = 0; i < 32; ++i) {
        uint32_t bit = 1u << i;
        if (t->active_faults_mask & bit)
            printf("[failsafe]   fault             : %s\n", fs_fault_name(bit));
    }
    printf("[failsafe] Active action      : %s (arbiter: %s)\n",
           fs_action_name(t->active_action), fs_arbiter_name(t->executing_arbiter));
    printf("[failsafe] RC link quality    : %u fps, timeout: %.1fs\n",
           t->rc_valid_frames_sec, (double)fs_params_get(p, FS_P_RC_TIMEOUT));
    printf("[failsafe] GNSS fix           : HDOP %.2f (max %.2f)\n",
           (double)t->gnss_hdop, (double)fs_params_get(p, FS_P_GNSS_HDOP_MAX));
    printf("[failsafe] Battery voltage    : %.2fV/cell, Crit: %.2fV\n",
           (double)t->batt_cell_min_v, (double)fs_params_get(p, FS_P_BATT_CRIT_V));
    printf("[failsafe] Geofence           : %s (dist to breach: %.1fm)\n",
           fs_params_get(p, FS_P_FENCE_ENABLE) != 0.0f ? "ENABLED" : "DISABLED",
           (double)t->distance_to_fence_m);
}

static void announce(uint32_t faults, const fs_param_block_t *p, const failsafe_telemetry_t *t)
{
    char text[80];

    for (int i = 0; i < 32; ++i) {
        uint32_t bit = 1u << i;
        if ((faults & bit) == 0u)
            continue;
        uint8_t sev = fs_statustext(bit, faults, p, t, text, sizeof text);
        printf("STATUSTEXT[%u %-9s] %s\n", sev, fs_severity_name(sev), text);
    }
}

int main(void)
{
    fs_param_store_t store;
    fs_param_block_t params;
    failsafe_telemetry_t tlm;
    uint8_t frame[FS_FRAME_LEN];
    char errors[512];
    fs_store_status_t rc;
    fs_decision_t d;
    int bank, bad;

    /* --- Перше вмикання: сектор стертий, беремо заводські значення --- */
    fs_store_init(&store);
    rc = fs_store_load(&store, &params, &bank);
    printf("boot: load -> %s, bank=%d\n", fs_store_status_str(rc), bank);

    /* Оператор підтягує конфігурацію під важчий планер і довшу місію. */
    if (fs_params_set_by_name(&params, "FS_FENCE_RADIUS", 4000.0f) != FS_PARAM_OK)
        printf("param: FS_FENCE_RADIUS відхилено\n");
    if (fs_params_set_by_name(&params, "FS_BATT_CRIT_V", 2.9f) != FS_PARAM_OK)
        printf("param: FS_BATT_CRIT_V=2.90 відхилено (%s)\n",
               fs_param_status_str(FS_PARAM_ERR_RANGE));

    rc = fs_store_save(&store, &params);
    printf("save: %s, active bank=%d, seq=%lu\n",
           fs_store_status_str(rc), store.active, (unsigned long)store.last_seq);

    /* --- Деградація комірки в активному банку: CRC ловить, живе дзеркало --- */
    fs_store_flip_bit(&store, store.active, FS_HDR_SIZE + 4u * FS_P_FENCE_RADIUS, 3);
    rc = fs_store_load(&store, &params, &bank);
    printf("reload after bit-flip: %s, bank=%d, radius=%.0f\n",
           fs_store_status_str(rc), bank, (double)fs_params_get(&params, FS_P_FENCE_RADIUS));

    /* --- Передпольотна валідація --- */
    bad = fs_params_validate(&params, RTL_ALT_M, errors, sizeof errors);
    printf("pre-arm: %d порушень\n%s", bad, bad ? errors : "");

    /* --- Сценарій: 3.5 км від дому, обрив керування на тлі глушіння GNSS --- */
    memset(&tlm, 0, sizeof tlm);
    tlm.timestamp_us = 742315000ull;
    tlm.rc_valid_frames_sec = 0;
    tlm.gnss_hdop = 4.8f;
    tlm.batt_cell_min_v = 3.62f;
    tlm.distance_to_fence_m = 500.0f;
    tlm.active_faults_mask = FS_FAULT_RC_LOST | FS_FAULT_GNSS_HDOP |
                             FS_FAULT_GNSS_LOST | FS_FAULT_EKF_DIVERGED;

    d = fs_decide(tlm.active_faults_mask, &params);
    tlm.active_action = d.action;
    tlm.executing_arbiter = d.arbiter;

    printf("\nnsh> failsafe status\n");
    cli_status(&params, &tlm);
    printf("\n");
    announce(tlm.active_faults_mask, &params, &tlm);

    /* Кадр FAILSAFE_STATUS у ефір і назад — так його бачить наземна станція. */
    if (fs_frame_pack(&tlm, frame, sizeof frame) == FS_FRAME_LEN) {
        failsafe_telemetry_t back;
        printf("\nFAILSAFE_STATUS (%u B):", FS_FRAME_LEN);
        for (uint32_t i = 0; i < FS_FRAME_LEN; ++i)
            printf(" %02X", frame[i]);
        printf("\n");
        printf("decode: %s\n", fs_frame_unpack(frame, FS_FRAME_LEN, &back)
                                   ? fs_action_name(back.active_action)
                                   : "REJECTED");
    }

    /* Зв'язок відновився: після гістерезису повертаємо ручне керування. */
    {
        char text[80];
        uint8_t sev = fs_statustext_recovered(&params, text, sizeof text);
        printf("STATUSTEXT[%u %-9s] %s\n", sev, fs_severity_name(sev), text);
    }

    return 0;
}
