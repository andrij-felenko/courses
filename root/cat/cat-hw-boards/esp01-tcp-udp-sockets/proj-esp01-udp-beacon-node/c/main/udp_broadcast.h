/**
 * @file udp_broadcast.h
 * @brief Оголошення функцій та структур для роботи з неблокуючим UDP-сокетом в ESP-IDF.
 */

#ifndef UDP_BROADCAST_H
#define UDP_BROADCAST_H

#include <stdint.h>
#include <stdbool.h>

#define UDP_PORT           3333         // Локальний та віддалений порт для UDP-пакетів
#define BROADCAST_IP_ADDR  "255.255.255.255" // Широкомовна адреса підмережі
#define RX_BUFFER_SIZE     256          // Розмір буфера прийому датаграм

/**
 * @brief Структура бінарного кадру телеметрії модуля ESP-01
 */
typedef struct __attribute__((packed)) {
    uint32_t device_id;    // Унікальний ідентифікатор пристрою
    uint32_t sequence;     // Порядковий номер пакета
    uint32_t uptime_ms;    // Час роботи мікроконтролера в мілісекундах
    uint8_t  payload_len;   // Довжина корисного навантаження
    char     data[32];     // Текстовий статус або корисні дані
} telemetry_pkt_t;

/**
 * @brief Ініціалізація та відкриття неблокуючого широкомовного UDP-сокета
 * 
 * @return int Дескриптор сокета (sock_fd) або -1 при помилці
 */
int udp_socket_create(void);

/**
 * @brief Відправка широкомовної датаграми у мережу
 * 
 * @param sock_fd Дескриптор сокета
 * @param pkt Вказівник на структуру пакета телеметрії
 * @return bool true у разі успішної відправки, false при помилці
 */
bool udp_socket_send_broadcast(int sock_fd, const telemetry_pkt_t *pkt);

/**
 * @brief Неблокуючий прийом вхідних датаграм
 * 
 * @param sock_fd Дескриптор сокета
 * @param buffer Буфер для збереження отриманих даних
 * @param max_len Максимальний розмір буфера
 * @return int Кількість прочитаних байтів, 0 якщо даних немає, або -1 при критичній помилці
 */
int udp_socket_receive(int sock_fd, uint8_t *buffer, size_t max_len);

/**
 * @brief Безпечне закриття сокета та вивільнення мережевих ресурсів
 * 
 * @param sock_fd Вказівник на дескриптор сокета (після закриття обнуляється)
 */
void udp_socket_close(int *sock_fd);

#endif // UDP_BROADCAST_H
