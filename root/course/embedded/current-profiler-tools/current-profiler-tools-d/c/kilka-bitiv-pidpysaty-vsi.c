// Номер поточної фази двійково на 3 GPIO → 3 цифрові входи приладу
typedef enum { PH_SLEEP=0, PH_BOOT=1, PH_SENSE=2, PH_TX=3, PH_FLASH=4 } phase_t;

#define PH_GPIO0 25
#define PH_GPIO1 26
#define PH_GPIO2 27

static inline void phase_set(phase_t p) {
    uint32_t set = 0, clr = 0;
    ((p >> 0) & 1 ? set : clr) |= (1u << PH_GPIO0);
    ((p >> 1) & 1 ? set : clr) |= (1u << PH_GPIO1);
    ((p >> 2) & 1 ? set : clr) |= (1u << PH_GPIO2);
    REG_WRITE(GPIO_OUT_W1TS_REG, set);   // одночасно: підняти потрібні біти
    REG_WRITE(GPIO_OUT_W1TC_REG, clr);   //            й опустити решту
}

void cycle(void) {
    phase_set(PH_BOOT);   boot_init();
    phase_set(PH_SENSE);  sensor_read();
    phase_set(PH_TX);     wifi_send(pkt, len);
    phase_set(PH_FLASH);  log_append(pkt, len);
    phase_set(PH_SLEEP);  enter_deep_sleep();
}
