#ifndef BOOT_TRIGGER_H
#define BOOT_TRIGGER_H

#include <stddef.h>
#include <stdint.h>

/* Магічні маркери в резервних регістрах RTC. ASCII у полі значення — щоб
   при відлагодженні їх було видно в дампі пам'яті. */
#define BOOT_MAGIC_FORCE_BOOTLOADER 0x424C6F6Fu /* "BLoo" — лишитись у завантажувачі */
#define BOOT_MAGIC_BETAFLIGHT_DFU   0x42465400u /* "BFT\0" — стрибок у системний ROM DFU */
#define BOOT_MAGIC_USB_TOUCH        0x544F5543u /* "TOUC" — 1200 bps touch */
#define BOOT_MAGIC_ROLLBACK         0x524F4C4Cu /* "ROLL" — аварійний відкат */

/* Пауза між рішенням перезапуститись і самим скиданням: хост має встигнути
   отримати COMMAND_ACK і закрити свій кінець USB-порту. */
#define BOOT_REBOOT_DELAY_MS 100u

void     boot_trigger_arm(uint32_t magic);
uint32_t boot_trigger_take(void);
void     boot_trigger_arm_rollback(void);
int      boot_trigger_take_rollback(void);

/* Негайне скидання ядра — так виходить завантажувач після прошивки. */
void boot_trigger_reset(void);

/* Відкладене скидання: маркер ставимо зараз, скидаємось із головного циклу. */
void boot_trigger_request_reboot(uint32_t magic, uint32_t now_ms);
void boot_trigger_service(uint32_t now_ms);

/* Метод 1: перехоплення класових запитів USB CDC-ACM. */
void cdc_set_line_coding(const uint8_t buf[7], uint32_t now_ms);
void cdc_set_control_line_state(uint16_t value, uint32_t now_ms);

/* Обробник DFU_DETACH з боку польотної прошивки (стан appIDLE). */
void boot_trigger_handle_detach(uint16_t detach_timeout_ms, uint32_t now_ms);

/* Метод 3: MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN у COMMAND_LONG. */
#define MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN 246u
#define MAVLINK_COMMAND_LONG_LEN 33u

typedef enum {
    MAV_RESULT_ACCEPTED             = 0u,
    MAV_RESULT_TEMPORARILY_REJECTED = 1u,
    MAV_RESULT_DENIED               = 2u,
    MAV_RESULT_UNSUPPORTED          = 3u,
    MAV_RESULT_FAILED               = 4u
} mav_result_t;

mav_result_t mavlink_handle_command_long(const uint8_t *payload, size_t len,
                                         uint8_t our_system, uint8_t our_component,
                                         uint32_t now_ms);

#endif /* BOOT_TRIGGER_H */
