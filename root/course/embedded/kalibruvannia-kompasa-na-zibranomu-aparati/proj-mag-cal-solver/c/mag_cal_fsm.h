/* ==========================================================================
 *  mag_cal_fsm.h — скінченний автомат процедури калібрування
 *
 *      IDLE ──старт──► COLLECTING ──покриття 80 %──► SOLVING
 *                          ▲   │                        │
 *                тайм-аут  │   └──60 с без точок──► IDLE│
 *                                                       ├─RMS > 3.0──► REJECTED
 *                                                       └─RMS ≤ 3.0──► VALIDATING
 *                                                                          │
 *                                                        cond(W) < 2.5 і   │
 *                                                        запис із CRC32 ───► SAVED
 *
 *  Автомат нічого не знає ні про RTOS, ні про драйвери: розв'язувач йому
 *  подають ззовні готовим результатом, бо працює той 2–4 мс і не має права
 *  крутитися всередині виклику з сенсорного потоку.
 * ========================================================================== */
#ifndef MAG_CAL_FSM_H
#define MAG_CAL_FSM_H

#include "mag_cal_collector.h"
#include "mag_cal_solver.h"
#include "mag_cal_storage.h"
#include "mag_cal_telemetry.h"
#include "mag_cal_types.h"

typedef enum {
    MAG_CAL_STATE_IDLE = 0,
    MAG_CAL_STATE_COLLECTING,
    MAG_CAL_STATE_SOLVING,
    MAG_CAL_STATE_VALIDATING,
    MAG_CAL_STATE_REJECTED,
    MAG_CAL_STATE_SAVED
} mag_cal_state_t;

typedef struct {
    mag_cal_state_t          state;
    mag_cal_collector_t      collector;
    mag_cal_result_t         active;      /* чинні коефіцієнти польоту */
    mag_cal_result_t         candidate;   /* результат останнього прогону */
    mag_cal_telemetry_t      tm;
    mag_cal_solve_status_t   last_solve;
    mag_cal_storage_status_t last_storage;
    bool                     mag_fault;   /* статус EKF_MAG_FAULT */
    uint32_t                 state_since_ms;
} mag_cal_fsm_t;

const char *mag_cal_state_str(mag_cal_state_t st);

void mag_cal_fsm_init(mag_cal_fsm_t *fsm, uint8_t compass_id,
                      uint8_t system_id, uint8_t component_id,
                      float earth_field_ut);

/* Старт плати: підняти калібрування з Flash, звірити CRC32 і нев'язку.
 * Невдача не зупиняє політ автоматично — вона запалює прапорець відмови
 * й діод, а рішення «не злітати» приймає гейт озброєння. */
mag_cal_storage_status_t mag_cal_fsm_boot(mag_cal_fsm_t *fsm, uint32_t now_ms);

bool mag_cal_fsm_start(mag_cal_fsm_t *fsm, uint32_t now_ms);
void mag_cal_fsm_cancel(mag_cal_fsm_t *fsm, uint32_t now_ms);

/* Швидкий шлях сенсорного потоку */
bool mag_cal_fsm_push(mag_cal_fsm_t *fsm, vec3_t raw, vec3_t gyro_rad_s,
                      uint32_t now_ms);

/* Фоновий потік: чи час рахувати, і передача готового результату */
bool mag_cal_fsm_ready_to_solve(const mag_cal_fsm_t *fsm);
void mag_cal_fsm_begin_solve(mag_cal_fsm_t *fsm, uint32_t now_ms);
void mag_cal_fsm_submit(mag_cal_fsm_t *fsm, mag_cal_solve_status_t status,
                        const mag_cal_result_t *result, uint32_t now_ms);

/* Періодичне обслуговування: тайм-аут бездіяльності й телеметрія прогресу */
void mag_cal_fsm_service(mag_cal_fsm_t *fsm, uint32_t now_ms);

vec3_t mag_cal_fsm_correct(const mag_cal_fsm_t *fsm, vec3_t raw);
bool   mag_cal_fsm_arming_allowed(const mag_cal_fsm_t *fsm);

/* --- Порт плати: сигналізація відмови компаса --- */
void mag_cal_board_fault_led(bool on);

#endif /* MAG_CAL_FSM_H */
