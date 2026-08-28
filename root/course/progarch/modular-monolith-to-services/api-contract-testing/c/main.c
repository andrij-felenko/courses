/* C: Обробник станів Провайдера (Provider State Callbacks) */
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    const char *state_name;
    bool (*setup_func)(const char *params_json);
} provider_state_entry_t;

/* Хук підготовки даних для існуючого пристрою 105 */
static bool setup_device_105_exists(const char *params_json) {
    printf("[PACT STATE SETUP] Clearing test DB & inserting device_id=105 with telemetry...\n");
    /* Виконання SQL: INSERT INTO telemetry (device_id, temp) VALUES (105, 22.5); */
    return true;
}

/* Хук підготовки даних для відсутнього пристрою 99999 */
static bool setup_device_99999_absent(const char *params_json) {
    printf("[PACT STATE SETUP] Ensuring device_id=99999 is DELETED from test DB...\n");
    /* Виконання SQL: DELETE FROM telemetry WHERE device_id = 99999; */
    return true;
}

/* Таблиця реєстрації станів провайдера */
static provider_state_entry_t STATE_REGISTRY[] = {
    { "device with ID 105 has historical telemetry readings", setup_device_105_exists },
    { "device with ID 99999 does not exist", setup_device_99999_absent }
};

/* Головний обробник State Setup HTTP запиту від pact-verifier */
bool handle_pact_state_setup(const char *requested_state, const char *params_json) {
    size_t count = sizeof(STATE_REGISTRY) / sizeof(STATE_REGISTRY[0]);
    for (size_t i = 0; i < count; i++) {
        if (strcmp(STATE_REGISTRY[i].state_name, requested_state) == 0) {
            return STATE_REGISTRY[i].setup_func(params_json);
        }
    }
    printf("[PACT STATE ERROR] Unknown provider state requested: %s\n", requested_state);
    return false;
}
