/* Пакування сирої пари (R, S) у підпис формату ASN.1 DER — саме такий підпис
 * очікує TLS-стек у повідомленні CertificateVerify. */
#ifndef DER_SIG_H
#define DER_SIG_H

#include <stddef.h>
#include <stdint.h>

/* Найгірший випадок: SEQUENCE(2) + два INTEGER по (2 + 1 + 32) байтів. */
#define DER_SIG_MAX 72u

/* Повертає довжину записаного DER або 0, якщо буфер замалий. */
size_t der_encode_signature(const uint8_t raw[64], uint8_t *out, size_t cap);

#endif /* DER_SIG_H */
