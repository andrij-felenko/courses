// ── HAL: що вміє залізо; машина лише замовляє ────────────────────
extern void      tcpc_set_cc(cc_pull_t pull);   // виставити Rp / Rd / Open
extern cc_seen_t tcpc_cc_seen(void);            // що бачимо на CC (відн. нашої підтяжки)
extern bool      tcpc_vbus_present(void);       // VBUS вище порога під'єднання?
extern uint16_t  tcpc_vbus_mv(void);            // виміряна VBUS, мВ (уже відфільтрована)
extern void      tcpc_src_switch(bool on);      // ключ-джерело (пара back-to-back)
extern void      tcpc_snk_switch(bool on);      // ключ-стік (пара back-to-back)
extern void      tcpc_discharge(bool on);       // розрядний ключ на VBUS
extern void      tcpc_vconn(bool on);           // VCONN на другий пін CC
extern bool      tcpc_fault_oc(void);           // спрацював струмовий захист виходу?
extern void      pd_send(int msg);              // відправити PD-повідомлення
extern uint32_t  now_ms(void);
extern void      delay_us(uint32_t us);

enum { PD_PR_SWAP, PD_ACCEPT, PD_REJECT, PD_PS_RDY };

// Попередні оголошення (тіла — далі за текстом)
static void enter(port_t *p, tc_state_t s);
static void begin_swap(port_t *p);
static void prswap_tick(port_t *p);
