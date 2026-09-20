#ifndef HTTP_ADAPTER_H
#define HTTP_ADAPTER_H

#include "inbound_port.h"

/**
 * @file http_adapter.h
 * @brief Драйвуючий HTTP-адаптер (HTTP Driving Adapter).
 *
 * Приймає дескриптор клієнтського мережевого з'єднання, вичитує сирий HTTP-запит,
 * парсить метод, шлях, заголовки авторизації та тіло у форматі JSON, транслює дані
 * у доменну команду ядра та формує HTTP-відповідь із кодами 200, 400, 401 або 422.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Обробляє HTTP-з'єднання з дескриптора сокета через вхідний порт ядра.
 *
 * @param port Покажчик на контракт вхідного порту.
 * @param client_fd Дескриптор відкритого сокета клієнта.
 * @return int 0 при успішній обробці та відправці HTTP-відповіді, від'ємне число при системній помилці I/O.
 */
int http_adapter_handle_fd(inbound_port_t *port, int client_fd);

#ifdef __cplusplus
}
#endif

#endif /* HTTP_ADAPTER_H */
