#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

void process_dns_packet(uint8_t *buf, int *len, in_addr_t local_ip) {
    if (*len < 12) return; // Пакет пошкоджений або коротший за заголовок

    // Встановлюємо прапорці відповіді (QR=1, AA=1, RA=1, RCODE=0)
    buf[2] = 0x81;
    buf[3] = 0x80;

    // Встановлюємо кількість відповідей ANCOUNT = 1
    buf[6] = 0x00;
    buf[7] = 0x01;

    // Скидаємо NSCOUNT та ARCOUNT
    buf[8] = 0; buf[9] = 0;
    buf[10] = 0; buf[11] = 0;

    int offset = *len;

    // Дописуємо блок Resource Record
    buf[offset++] = 0xC0; // Вказівник на ім'я QNAME (зміщення 12)
    buf[offset++] = 0x0C;
    buf[offset++] = 0x00; // TYPE A (0x0001)
    buf[offset++] = 0x01;
    buf[offset++] = 0x00; // CLASS IN (0x0001)
    buf[offset++] = 0x01;
    buf[offset++] = 0x00; // TTL: 10 секунд (0x0000000A)
    buf[offset++] = 0x00;
    buf[offset++] = 0x00;
    buf[offset++] = 0x0A;
    buf[offset++] = 0x00; // RDLENGTH: 4 байти
    buf[offset++] = 0x04;

    // RDATA: копіюємо 4 байти IP-адреси
    memcpy(&buf[offset], &local_ip, 4);
    offset += 4;

    *len = offset;
}
