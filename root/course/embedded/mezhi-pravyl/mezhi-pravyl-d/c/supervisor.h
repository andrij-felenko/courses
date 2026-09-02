#ifndef SUPERVISOR_H
#define SUPERVISOR_H

#include "barrier.h"

/* Регламент взаємодії двох контурів: приймає кандидата від повільного
 * планувальника, перевіряє його на придатність і свіжість, зшиває з
 * попередньою уставкою без ривків і віддає бар'єру. */

typedef enum {
    CAND_OK,
    CAND_NOT_FINITE,   /* NaN або нескінченність у векторі уставки */
    CAND_OUT_OF_RANGE, /* поза фізичною обгорткою апарата */
    CAND_STALE         /* планувальник не встиг або завис */
} CandidateStatus;

typedef struct {
    Setpoint       candidate;
    bool           have_candidate;
    float          candidate_age_s;
    float          max_candidate_age_s;
    Setpoint       last_output;
    BarrierVerdict last_verdict;
    float          held_range_m;   /* останнє дійсне вимірювання далекоміра */
    int            dropouts;       /* тактів поспіль без даних лідара */
    int            max_dropouts;
    unsigned       verdict_changes;  /* метрика брязкання */
    unsigned       rejected_count;
} Supervisor;

typedef struct {
    Setpoint        out;
    BarrierResult   barrier;
    CandidateStatus cand_status;
} SupervisorTick;

void supervisor_init(Supervisor *s, const SafetyLimits *lim);

/* Виклик із повільного контуру, коли планувальник дорахував. */
void supervisor_submit(Supervisor *s, Setpoint candidate);

/* Виклик із жорсткого циклу керування, кожен такт. */
SupervisorTick supervisor_step(Supervisor *s, const RoverParams *p,
                               const SafetyLimits *lim,
                               const VehicleState *raw, float dt);

const char *supervisor_status_name(CandidateStatus s);

#endif /* SUPERVISOR_H */
