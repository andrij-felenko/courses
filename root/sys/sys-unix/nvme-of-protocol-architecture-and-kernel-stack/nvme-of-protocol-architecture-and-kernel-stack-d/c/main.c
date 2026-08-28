/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <endian.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/* Структури заголовків за специфікацією NVMe/TCP */
#pragma pack(push, 1)

struct nvme_tcp_hdr {
    uint8_t  type;       /* 0x04 = Command PDU */
    uint8_t  flags;      /* Прапори (HDigest, DDigest) */
    uint8_t  hlen;       /* Довжина заголовка (72 байти) */
    uint8_t  pdo;        /* Зміщення даних */
    uint32_t plen;       /* Повна довжина PDU */
};

struct nvme_tcp_cmd_pdu {
    struct nvme_tcp_hdr hdr;
    uint8_t  cmd[64];    /* 64-байтна капсула SQE NVMe */
};

#pragma pack(pop)

int send_nvme_read_command(int sock_fd, uint32_t nsid, uint64_t lba, uint16_t count) {
    struct nvme_tcp_cmd_pdu pdu;

    /* NVMe кодує кількість блоків як «N-1», тож нуль блоків — недійсний запит */
    if (count == 0) {
        return -1;
    }

    memset(&pdu, 0, sizeof(pdu));

    /* Налаштування PDU Header */
    pdu.hdr.type = 0x04; /* Command PDU */
    pdu.hdr.flags = 0;   /* Без хешів для спрощення */
    pdu.hdr.hlen = sizeof(struct nvme_tcp_cmd_pdu);
    pdu.hdr.pdo = 0;
    pdu.hdr.plen = htole32(sizeof(struct nvme_tcp_cmd_pdu));

    /* Заповнення 64-байтної SQE команди NVMe Read (Opcode 0x02) */
    pdu.cmd[0] = 0x02;                           /* Opcode: NVMe Read */
    *(uint16_t*)(pdu.cmd + 2) = htole16(0x1001);  /* Command ID */
    *(uint32_t*)(pdu.cmd + 4) = htole32(nsid);    /* Namespace ID */
    *(uint64_t*)(pdu.cmd + 40) = htole64(lba);    /* Starting LBA (CDW10/11) */
    *(uint16_t*)(pdu.cmd + 48) = htole16(count - 1); /* Number of Blocks (CDW12) */

    /* Байти 24..39 SQE — SGL-описувач буфера даних; тут він лишається нульовим,
       бо приклад показує лише формування самого PDU. */

    ssize_t sent = send(sock_fd, &pdu, sizeof(pdu), MSG_NOSIGNAL);
    if (sent < 0) {
        perror("Помилка відправки NVMe/TCP PDU");
        return -1;
    }
    if ((size_t)sent != sizeof(pdu)) {
        fprintf(stderr, "Часткова відправка PDU: %zd з %zu байт\n", sent, sizeof(pdu));
        return -1;
    }
    printf("Відправлено NVMe/TCP Read Command PDU: %zd байт\n", sent);
    return 0;
}
