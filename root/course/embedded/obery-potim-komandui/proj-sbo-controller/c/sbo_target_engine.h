/* sbo_target_engine.h — бортове ядро SBO: автомат станів і контракт платформи. */
#ifndef SBO_TARGET_ENGINE_H
#define SBO_TARGET_ENGINE_H

#include "sbo_protocol.h"

/* Діагностичні лінії для логічного аналізатора (§8 статті). */
typedef enum {
    SBO_DIAG_ARMED = 0,        /* рівень: високий, поки вузол у стані ARMED */
    SBO_DIAG_OP_EXEC,          /* імпульс 10 мкс: команду пропущено до приводу */
    SBO_DIAG_SECURITY_DROP     /* імпульс 50 мкс: кадр відкинуто валідатором */
} sbo_diag_line_t;

/* Це реалізує плата (у тестах — заглушка). Ядро не знає ні про GPIO, ні про реле. */
bool sbo_actuator_execute(uint16_t cmd_code, const uint8_t *payload, uint8_t payload_len);
void sbo_diag_set(sbo_diag_line_t line, bool level);
void sbo_diag_pulse(sbo_diag_line_t line, uint16_t width_us);

/* 20 байтів у .bss на вузол; поля лічильників скидає кожен init (§7). */
typedef struct {
    uint8_t  my_system_id;
    uint8_t  state;                     /* sbo_fsm_state_t, звужено до байта */
    uint8_t  locked_source_id;
    uint16_t locked_cmd_code;
    uint32_t active_token;
    uint32_t arm_expiry_timestamp_ms;
    uint32_t prng_seed;
    uint16_t select_count;
    uint16_t exec_count;
    uint16_t reject_count;
    uint16_t timeout_count;
} sbo_target_context_t;

/* Після кожного старту (у тому числі після brownout-скидання) вузол — IDLE,
 * а токен народжується заново: у Flash його не зберігаємо ніколи. */
void sbo_target_init(sbo_target_context_t *ctx, uint8_t system_id, uint32_t initial_seed);

/* Викликати кожні 10..50 мс. true — щойно знешкодило за таймером. */
bool sbo_target_tick(sbo_target_context_t *ctx, uint32_t now_ms);

/* Обробка розібраного кадру. has_response = false означає «нічого не відсилати». */
sbo_error_t sbo_target_process_packet(sbo_target_context_t *ctx,
                                      const sbo_packet_t *rx,
                                      sbo_packet_t *tx,
                                      bool *has_response,
                                      uint32_t now_ms);

/* Вхід із радіоканалу: байти → перевірка → автомат → байти відповіді.
 * Саме це викликає RadioRxTask, вичитавши кадр із черги. */
sbo_error_t sbo_target_handle_frame(sbo_target_context_t *ctx,
                                    const uint8_t *in, size_t in_len,
                                    uint8_t *out, size_t out_cap, size_t *out_len,
                                    uint32_t now_ms);

#endif /* SBO_TARGET_ENGINE_H */
