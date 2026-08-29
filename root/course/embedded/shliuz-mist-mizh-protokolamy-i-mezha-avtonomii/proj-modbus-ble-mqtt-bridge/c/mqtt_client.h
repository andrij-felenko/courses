#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#include <stdint.h>

/* Мінімальний клієнт MQTT 3.1.1 — рівно те, що потрібно висхідному напрямку
 * шлюза: CONNECT, PUBLISH з QoS 1, PINGREQ і DISCONNECT.
 *
 * QoS 1 тут не примха: повідомлення знімається з черги лише після PUBACK,
 * тож обрив у момент передавання коштує повтору, а не втрати вимірювання.
 *
 * На виробництві сокет обгортають у TLS (наприклад, BIO OpenSSL поверх цього
 * ж дескриптора) — рамка пакетів від цього не міняється, тому тут ми лишаємо
 * чистий TCP, щоб було видно самі кадри протоколу.
 */

typedef struct mqtt_client mqtt_client_t;

/* NULL — під'єднатися не вдалося (немає маршруту, брокер відмовив у CONNACK). */
mqtt_client_t *mqtt_connect(const char *host, const char *port,
                            const char *client_id, uint16_t keepalive_s);

/* Ввічливе прощання з брокером і закриття сокета. */
void mqtt_disconnect(mqtt_client_t *c);

/* 0 — брокер підтвердив PUBACK; <0 — канал зламався, з'єднання треба піднімати заново. */
int mqtt_publish_qos1(mqtt_client_t *c, const char *topic, const char *payload);

/* Обслуговування keep-alive: шле PINGREQ, коли час, і вичитує те, що прилетіло.
 * <0 означає, що брокер не відповів на PINGREQ — канал мертвий, хоча TCP-сокет
 * може мовчки вважатися живим ще довгі хвилини. */
int mqtt_keepalive(mqtt_client_t *c);

#endif /* MQTT_CLIENT_H */
