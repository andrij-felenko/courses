#include "rule_engine.h"

#include <string.h>

/* ── доступ до регістрів ────────────────────────────────────────────── */

static bool write_register(rule_engine_t *e, uint8_t reg, int32_t value) {
    if (!reg_is_valid(reg)) { return false; }
    if (reg_is_sensor(reg)) {
        /* смуга давачів для правил Read-Only: пишуть її лише драйвери */
        e->registers[REG_ERROR_WORD] |= (int32_t)ERROR_BIT_RO_WRITE;
        return false;
    }
    e->registers[reg] = value;
    return true;
}

int32_t rule_engine_read(const rule_engine_t *e, uint8_t reg) {
    return reg_is_valid(reg) ? e->registers[reg] : 0;
}

void rule_engine_set_sensor(rule_engine_t *e, uint8_t reg, int32_t value) {
    if (reg_is_sensor(reg)) { e->registers[reg] = value; }
}

rule_error_t rule_engine_remote_write(rule_engine_t *e, uint8_t reg, int32_t value) {
    if (!reg_is_valid(reg)) { return ERR_REG_OUT_OF_RANGE; }
    if (reg_is_sensor(reg) || reg_is_timer(reg)) { return ERR_REG_READ_ONLY; }
    if (e->remote_inhibited[reg]) {
        e->registers[REG_ERROR_WORD] |= (int32_t)ERROR_BIT_REMOTE_BLOCKED;
        return ERR_REMOTE_INHIBITED;
    }
    e->registers[reg] = value;
    return ERR_NONE;
}

/* ── таймери ────────────────────────────────────────────────────────── */

static int timer_slot(rule_engine_t *e, uint8_t reg) {
    if (!reg_is_timer(reg)) {
        e->registers[REG_ERROR_WORD] |= (int32_t)ERROR_BIT_BAD_TIMER;
        return -1;
    }
    return (int)(reg - REG_TIMER_FIRST);
}

/* Різниця беззнакових лічильників сама переживає переповнення systick. */
static uint32_t elapsed_since(uint32_t now_ms, uint32_t start_ms) {
    return now_ms - start_ms;
}

static void mirror_timers(rule_engine_t *e, uint32_t now_ms) {
    for (unsigned i = 0; i < TIMER_COUNT; ++i) {
        const soft_timer_t *t = &e->timers[i];
        uint32_t left = 0;
        if (t->armed) {
            uint32_t gone = elapsed_since(now_ms, t->start_ms);
            left = (gone >= t->duration_ms) ? 0u : (t->duration_ms - gone);
        }
        e->registers[REG_TIMER_FIRST + i] = (int32_t)left;
    }
}

void rule_engine_hub_heartbeat(rule_engine_t *e, uint32_t now_ms) {
    soft_timer_t *lease = &e->timers[TIMER_HUB_LEASE];
    lease->armed       = true;
    lease->start_ms    = now_ms;
    lease->duration_ms = e->hub_lease_ms;
}

/* ── ініціалізація ──────────────────────────────────────────────────── */

void rule_engine_init(rule_engine_t *e, uint32_t hub_lease_ms, uint32_t now_ms) {
    memset(e, 0, sizeof(*e));
    e->hub_lease_ms = hub_lease_ms;
    e->last_eval_ms = now_ms;
    rule_engine_hub_heartbeat(e, now_ms);
}

/* ── умови ──────────────────────────────────────────────────────────── */

static bool eval_condition(rule_engine_t *e, const rule_descriptor_t *r, uint32_t now_ms) {
    if (r->cond_op == OP_TIMER_EXPIRED) {
        int slot = timer_slot(e, r->input_reg);
        if (slot < 0) { return false; }
        const soft_timer_t *t = &e->timers[slot];
        if (!t->armed) { return false; }
        return elapsed_since(now_ms, t->start_ms) > (uint32_t)r->threshold;
    }

    int32_t v = e->registers[r->input_reg];
    switch (r->cond_op) {
        case OP_ALWAYS:       return true;
        case OP_LESS_THAN:    return v < r->threshold;
        case OP_GREATER_THAN: return v > r->threshold;
        case OP_EQUAL:        return v == r->threshold;
        case OP_NOT_EQUAL:    return v != r->threshold;
        case OP_BIT_SET:      return (v & r->threshold) == r->threshold;
        case OP_BIT_CLEAR:    return (v & r->threshold) == 0;
        default:              return false;   /* валідація такого не пропускає */
    }
}

/* ── дії ────────────────────────────────────────────────────────────── */

static void enter_emergency(rule_engine_t *e) {
    /* Знеструмлюємо всю смугу виконавців. На залізі тут же скидається
       біт MOE в TIM1->BDTR, інакше ШІМ доживе до наступного такту. */
    for (uint8_t reg = REG_ACTUATOR_FIRST; reg <= REG_ACTUATOR_LAST; ++reg) {
        e->registers[reg] = 0;
    }
    e->emergency = true;
}

static void apply_action(rule_engine_t *e, const rule_descriptor_t *r) {
    switch (r->action_op) {
        case ACT_OUTPUT_SET:
            write_register(e, r->output_target, (r->action_param != 0) ? 1 : 0);
            break;

        case ACT_SET_SETPOINT:
            /* уставка передається цілими одиницями величини — розгортаємо в Q16.16 */
            write_register(e, r->output_target, (int32_t)r->action_param << 16);
            break;

        case ACT_ARM_TIMER: {
            int slot = timer_slot(e, r->output_target);
            if (slot < 0) { break; }
            soft_timer_t *t = &e->timers[slot];
            if (t->armed) { break; }   /* повторний завод не зсуває мітку запуску */
            t->armed       = true;
            t->start_ms    = e->last_eval_ms;
            t->duration_ms = (r->action_param > 0) ? (uint32_t)r->action_param : 0u;
            break;
        }

        case ACT_DISARM_TIMER: {
            int slot = timer_slot(e, r->output_target);
            if (slot < 0) { break; }
            e->timers[slot].armed = false;
            e->registers[REG_TIMER_FIRST + slot] = 0;
            break;
        }

        case ACT_EMERGENCY_STOP:
            enter_emergency(e);
            break;

        case ACT_INHIBIT_REMOTE:
            if (reg_is_valid(r->output_target)) {
                e->remote_inhibited[r->output_target] = true;
            }
            break;

        default:
            break;
    }
}

/* Автоскидання (RULE_FLAG_INVERT_ACTION): умова стала хибною — знімаємо те,
   що це саме правило поставило. Аварійний стоп зворотної дії не має. */
static void undo_action(rule_engine_t *e, const rule_descriptor_t *r) {
    switch (r->action_op) {
        case ACT_OUTPUT_SET:
            write_register(e, r->output_target, (r->action_param != 0) ? 0 : 1);
            break;
        case ACT_ARM_TIMER: {
            int slot = timer_slot(e, r->output_target);
            if (slot < 0) { break; }
            e->timers[slot].armed = false;
            e->registers[REG_TIMER_FIRST + slot] = 0;
            break;
        }
        case ACT_INHIBIT_REMOTE:
            if (reg_is_valid(r->output_target)) {
                e->remote_inhibited[r->output_target] = false;
            }
            break;
        default:
            break;
    }
}

/* ── такт обчислення ────────────────────────────────────────────────── */

static void eval_rule(rule_engine_t *e, uint8_t slot, uint32_t now_ms) {
    const rule_descriptor_t *r = &e->rules[slot];
    if (r->rule_id == 0 || (r->flags & RULE_FLAG_ENABLED) == 0) { return; }

    bool critical = (r->flags & RULE_FLAG_SAFETY_CRITICAL) != 0;
    /* У режимі блокування аварії живими лишаються самі інваріанти безпеки. */
    if (e->emergency && !critical) { return; }

    uint32_t bit = 1u << slot;

    /* Зафіксоване правило тримає дію, поки не буде явного скидання аварії. */
    if ((e->latched & bit) != 0) {
        apply_action(e, r);
        return;
    }

    bool fallback_only = (r->flags & RULE_FLAG_FALLBACK_ACTIVE) != 0;
    bool cond = (fallback_only && !e->fallback) ? false : eval_condition(e, r, now_ms);

    if (cond) {
        apply_action(e, r);
        e->fired |= bit;
        if ((r->flags & RULE_FLAG_LATCHING) != 0) { e->latched |= bit; }
    } else {
        if ((e->fired & bit) != 0 && (r->flags & RULE_FLAG_INVERT_ACTION) != 0) {
            undo_action(e, r);
        }
        e->fired &= ~bit;
    }
}

void rule_engine_tick(rule_engine_t *e, uint32_t now_ms) {
    e->last_eval_ms = now_ms;

    /* Оренда керування: серцебиття хаба заводить свій таймер наново. */
    const soft_timer_t *lease = &e->timers[TIMER_HUB_LEASE];
    e->fallback = !lease->armed || elapsed_since(now_ms, lease->start_ms) > lease->duration_ms;

    mirror_timers(e, now_ms);

    /* Два проходи: спершу критичні інваріанти, далі решта. Порядок гнізд
       у межах проходу — порядок таблиці, тож пізніше правило має останнє слово. */
    for (int pass = 0; pass < 2; ++pass) {
        for (uint8_t i = 0; i < e->rule_count; ++i) {
            bool critical = (e->rules[i].flags & RULE_FLAG_SAFETY_CRITICAL) != 0;
            if ((pass == 0) != critical) { continue; }
            eval_rule(e, i, now_ms);
        }
    }

    int32_t status = 0;
    if (e->fallback)  { status |= (int32_t)STATUS_BIT_FALLBACK; }
    if (e->emergency) { status |= (int32_t)STATUS_BIT_EMERGENCY; }
    if (e->latched)   { status |= (int32_t)STATUS_BIT_LATCHED; }
    e->registers[REG_STATUS_WORD] = status;
}

void rule_engine_reset_alarm(rule_engine_t *e) {
    e->latched   = 0;
    e->fired     = 0;
    e->emergency = false;
    e->registers[REG_STATUS_WORD] &= ~(int32_t)(STATUS_BIT_EMERGENCY | STATUS_BIT_LATCHED);
    e->registers[REG_ERROR_WORD] = 0;
    /* Причина аварії не зникає: якщо умова досі істинна, критичне правило
       спрацює на найближчому ж такті. */
}

/* ── семантична верифікація таблиці ─────────────────────────────────── */

static bool cond_op_known(uint8_t op) {
    return op >= OP_ALWAYS && op <= OP_TIMER_EXPIRED;
}

static bool action_op_known(uint8_t op) {
    return op >= ACT_OUTPUT_SET && op <= ACT_INHIBIT_REMOTE;
}

static rule_error_t check_targets(const rule_descriptor_t *r) {
    if (!reg_is_valid(r->input_reg) || !reg_is_valid(r->output_target)) {
        return ERR_REG_OUT_OF_RANGE;
    }
    if (r->cond_op == OP_TIMER_EXPIRED && !reg_is_timer(r->input_reg)) {
        return ERR_REG_OUT_OF_RANGE;
    }
    switch (r->action_op) {
        case ACT_OUTPUT_SET:
            if (!reg_is_actuator(r->output_target)) { return ERR_REG_OUT_OF_RANGE; }
            break;
        case ACT_SET_SETPOINT:
            if (!reg_is_setpoint(r->output_target)) { return ERR_REG_OUT_OF_RANGE; }
            break;
        case ACT_ARM_TIMER:
        case ACT_DISARM_TIMER:
            /* гніздо оренди хаба правилам не належить */
            if (!reg_is_timer(r->output_target) || r->output_target == REG_HUB_LEASE) {
                return ERR_REG_OUT_OF_RANGE;
            }
            break;
        case ACT_INHIBIT_REMOTE:
            if (!reg_is_actuator(r->output_target) && !reg_is_setpoint(r->output_target)) {
                return ERR_REG_OUT_OF_RANGE;
            }
            break;
        default:
            break;
    }
    return ERR_NONE;
}

rule_error_t rule_engine_validate_table(const rule_engine_t *e,
                                        const rule_descriptor_t *table, uint8_t count) {
    if (count > MAX_RULES_COUNT) { return ERR_BUFFER_OVERFLOW; }

    for (uint8_t i = 0; i < count; ++i) {
        const rule_descriptor_t *r = &table[i];
        if (r->rule_id == 0)                        { return ERR_BAD_RULE_ID; }
        if (r->reserved != 0)                       { return ERR_BAD_RESERVED; }
        if ((r->flags & ~RULE_FLAGS_KNOWN_MASK))    { return ERR_BAD_FLAGS; }
        if (!cond_op_known(r->cond_op))             { return ERR_BAD_OPCODE; }
        if (!action_op_known(r->action_op))         { return ERR_BAD_OPCODE; }

        rule_error_t err = check_targets(r);
        if (err != ERR_NONE) { return err; }

        for (uint8_t j = 0; j < i; ++j) {
            if (table[j].rule_id == r->rule_id) { return ERR_DUPLICATE_ID; }
        }
    }

    /* Жодне чинне критичне правило не має права зникнути чи змінитися:
       мережева команда не вимикає захист від перегріву. */
    for (uint8_t i = 0; i < e->rule_count; ++i) {
        const rule_descriptor_t *cur = &e->rules[i];
        if ((cur->flags & RULE_FLAG_SAFETY_CRITICAL) == 0) { continue; }

        bool preserved = false;
        for (uint8_t j = 0; j < count; ++j) {
            if (table[j].rule_id != cur->rule_id) { continue; }
            preserved = memcmp(&table[j], cur, sizeof(*cur)) == 0;
            break;
        }
        if (!preserved) { return ERR_SAFETY_VIOLATION; }
    }

    return ERR_NONE;
}

void rule_engine_commit_table(rule_engine_t *e,
                              const rule_descriptor_t *table, uint8_t count) {
    uint32_t state = rule_critical_enter();
    memcpy(e->rules, table, (size_t)count * sizeof(rule_descriptor_t));
    if (count < MAX_RULES_COUNT) {
        memset(&e->rules[count], 0,
               (MAX_RULES_COUNT - count) * sizeof(rule_descriptor_t));
    }
    e->rule_count = count;
    /* Гнізда змінили нумерацію — маски спрацювань більше не про ці правила. */
    e->fired = 0;
    e->latched = 0;
    rule_critical_exit(state);
}
