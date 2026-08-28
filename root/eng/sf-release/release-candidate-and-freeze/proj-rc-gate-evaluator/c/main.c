#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_DEFECTS_LIMIT 0
#define MAX_FLASH_BYTES (8 * 1024 * 1024 + 512 * 1024) /* 8.5 MiB */
#define MAX_RAM_BYTES   (384 * 1024)                    /* 384 KiB */
#define MAX_BOOT_TIME_MS 250
#define MAX_SLEEP_CURRENT_UA 15.0f

typedef struct {
    uint32_t flash_used_bytes;
    uint32_t ram_used_bytes;
    uint32_t boot_time_ms;
    float sleep_current_ua;
    uint32_t hil_total_tests;
    uint32_t hil_passed_tests;
    uint32_t critical_defects_count;
    bool hardfault_occurred;
    bool watchdog_reset_occurred;
} ReleaseCandidateMetrics;

typedef enum {
    DECISION_PROMOTED_GA = 0,
    DECISION_REJECTED_BUDGET_OVERRUN = 1,
    DECISION_REJECTED_HIL_FAILURE = 2,
    DECISION_REJECTED_CRITICAL_BUGS = 3,
    DECISION_REJECTED_SYSTEM_FAULT = 4
} GateDecision;

typedef struct {
    GateDecision decision;
    char reason[256];
    char candidate_sha256[65];
} EvaluationResult;

GateDecision evaluate_release_candidate(const ReleaseCandidateMetrics* metrics,
                                        const char* binary_sha256,
                                        EvaluationResult* out_result) {
    if (!metrics || !binary_sha256 || !out_result) {
        return DECISION_REJECTED_SYSTEM_FAULT;
    }

    memset(out_result, 0, sizeof(EvaluationResult));
    strncpy(out_result->candidate_sha256, binary_sha256, 64);

    /* 1. Перевірка блокуючих дефектів */
    if (metrics->critical_defects_count > MAX_DEFECTS_LIMIT) {
        out_result->decision = DECISION_REJECTED_CRITICAL_BUGS;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: виявлено %u критичних дефектів (ліміт: %u)",
                 metrics->critical_defects_count, MAX_DEFECTS_LIMIT);
        return out_result->decision;
    }

    /* 2. Перевірка апаратних збоїв на стенді */
    if (metrics->hardfault_occurred || metrics->watchdog_reset_occurred) {
        out_result->decision = DECISION_REJECTED_SYSTEM_FAULT;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: зафіксовано фатальні збої (HardFault=%d, WDT_Reset=%d)",
                 metrics->hardfault_occurred, metrics->watchdog_reset_occurred);
        return out_result->decision;
    }

    /* 3. Перевірка 100% успішності HIL-тестів */
    if (metrics->hil_total_tests == 0 || metrics->hil_passed_tests < metrics->hil_total_tests) {
        out_result->decision = DECISION_REJECTED_HIL_FAILURE;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: HIL-тести не пройдено на 100%% (%u з %u успішних)",
                 metrics->hil_passed_tests, metrics->hil_total_tests);
        return out_result->decision;
    }

    /* 4. Перевірка бюджетів флеш-пам'яті та ОЗП */
    if (metrics->flash_used_bytes > MAX_FLASH_BYTES) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: перевищення Flash ROM (%u байт > %u ліміт)",
                 metrics->flash_used_bytes, MAX_FLASH_BYTES);
        return out_result->decision;
    }

    if (metrics->ram_used_bytes > MAX_RAM_BYTES) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: перевищення SRAM (%u байт > %u ліміт)",
                 metrics->ram_used_bytes, MAX_RAM_BYTES);
        return out_result->decision;
    }

    /* 5. Перевірка енергоспоживання та часу запуску */
    if (metrics->sleep_current_ua > MAX_SLEEP_CURRENT_UA) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: струм сну %.2f мкА перевищує поріг %.2f мкА",
                 metrics->sleep_current_ua, MAX_SLEEP_CURRENT_UA);
        return out_result->decision;
    }

    if (metrics->boot_time_ms > MAX_BOOT_TIME_MS) {
        out_result->decision = DECISION_REJECTED_BUDGET_OVERRUN;
        snprintf(out_result->reason, sizeof(out_result->reason),
                 "Відхилено: час завантаження %u мс перевищує ліміт %u мс",
                 metrics->boot_time_ms, MAX_BOOT_TIME_MS);
        return out_result->decision;
    }

    out_result->decision = DECISION_PROMOTED_GA;
    snprintf(out_result->reason, sizeof(out_result->reason),
             "СХВАЛЕНО: Всі вихідні критерії виконано. Кандидат готовий до промоції в GA.");
    return DECISION_PROMOTED_GA;
}

int main(void) {
    ReleaseCandidateMetrics rc_sample = {
        .flash_used_bytes = 4194304, /* 4 MiB */
        .ram_used_bytes = 196608,   /* 192 KiB */
        .boot_time_ms = 180,
        .sleep_current_ua = 11.4f,
        .hil_total_tests = 1450,
        .hil_passed_tests = 1450,
        .critical_defects_count = 0,
        .hardfault_occurred = false,
        .watchdog_reset_occurred = false
    };

    const char* sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
    EvaluationResult res;

    GateDecision status = evaluate_release_candidate(&rc_sample, sha256, &res);

    printf("=== РЕЗУЛЬТАТ АРБІТРАЖУ РЕЛІЗ-КАНДИДАТА ===\n");
    printf("Статус рішення: %d\n", status);
    printf("Обґрунтування : %s\n", res.reason);
    printf("SHA-256 образу: %s\n", res.candidate_sha256);

    return (status == DECISION_PROMOTED_GA) ? 0 : 1;
}
