#ifndef BLE_SCAN_H
#define BLE_SCAN_H

#include <stdint.h>

/* Пасивне сканування BLE через сирий HCI-сокет ядра Linux.
 *
 * Давачі на рухомих підшипниках не тримають з'єднання: вони прокидаються,
 * кидають рекламний кадр і засинають. Шлюзу залишається слухати ефір, тому
 * ніякого GATT-з'єднання тут немає — лише розбір рекламних кадрів.
 *
 * Потрібні права CAP_NET_RAW (відкрити сокет) і CAP_NET_ADMIN (віддати
 * контролеру команду сканування). Bluetoothd на цьому ж адаптері сканувати
 * одночасно не повинен — інакше він перезапише параметри сканування.
 */

typedef struct ble_scanner ble_scanner_t;

typedef struct {
    uint8_t addr[6];        /* адреса давача, молодшим байтом уперед, як у HCI */
    float temperature_c;
    uint8_t battery_pct;
    int8_t rssi_dbm;
} ble_sample_t;

/* hci_index — номер адаптера (hci0 → 0). */
ble_scanner_t *ble_open(int hci_index);
void ble_close(ble_scanner_t *s);

/*  1 — здобуто зразок нашого давача,
 *  0 — за timeout_ms нічого придатного не прилетіло,
 * -1 — сокет помер (адаптер вимкнули чи забрали). */
int ble_next_sample(ble_scanner_t *s, ble_sample_t *out, int timeout_ms);

#endif /* BLE_SCAN_H */
