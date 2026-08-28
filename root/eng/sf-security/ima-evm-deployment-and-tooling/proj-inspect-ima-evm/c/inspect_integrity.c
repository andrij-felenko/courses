/* inspect_integrity.c - Інспекція атрибутів IMA/EVM мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <sys/xattr.h>

#define IMA_XATTR_DIGEST_NG 0x02
#define EVMSIG_XATTR_DIGEST 0x04
#define IMA_ASYM_DIGSIG     0x05

struct signature_v2_hdr {
    uint8_t type;
    uint8_t version;
    uint8_t hash_algo;
    uint32_t keyid;
    uint16_t sig_size;
} __attribute__((packed));

static const char* algo_name(uint8_t algo) {
    switch (algo) {
        case 1: return "SHA-1";
        case 2: return "RIPEMD160";
        case 4: return "SHA-256";
        case 5: return "SHA-384";
        case 6: return "SHA-512";
        default: return "Невідомий";
    }
}

static void inspect_ima_xattr(const char *filepath) {
    uint8_t buffer[1024];
    ssize_t res = getxattr(filepath, "security.ima", buffer, sizeof(buffer));
    
    if (res < 0) {
        if (errno == ENODATA) {
            printf("[IMA] Атрибут security.ima відсутній у файлі\n");
        } else {
            perror("[IMA] Помилка системного виклику getxattr");
        }
        return;
    }

    if (res == 0) {
        printf("[IMA] Атрибут security.ima існує, але має порожній вміст\n");
        return;
    }

    uint8_t type = buffer[0];
    printf("[IMA] Зчитано %zd байт. Заголовочний тип атрибута: 0x%02x\n", res, type);

    if (type == IMA_XATTR_DIGEST_NG && res >= 2) {
        uint8_t algo = buffer[1];
        printf("  -> Формат: DIGEST_NG (необроблений криптографічний хеш)\n");
        printf("  -> Алгоритм хешування: %s (id: %d)\n", algo_name(algo), algo);
        printf("  -> Хеш вмісту (hex): ");
        for (ssize_t i = 2; i < res; i++) {
            printf("%02x", buffer[i]);
        }
        printf("\n");
    } else if ((type == EVMSIG_XATTR_DIGEST || type == IMA_ASYM_DIGSIG) &&
               res >= (ssize_t)sizeof(struct signature_v2_hdr)) {
        struct signature_v2_hdr *hdr = (struct signature_v2_hdr*)buffer;
        uint32_t keyid = __builtin_bswap32(hdr->keyid);
        uint16_t sig_len = __builtin_bswap16(hdr->sig_size);
        printf("  -> Формат: Асиметричний цифровий підпис (версія %d)\n", hdr->version);
        printf("  -> Алгоритм хешування: %s\n", algo_name(hdr->hash_algo));
        printf("  -> Key ID відкритого ключа у брелоку .ima: 0x%08x\n", keyid);
        printf("  -> Розмір цифрового підпису: %u байт\n", sig_len);
    } else {
        printf("  -> Формат: Невідомий або застарілий тип заголовка атрибута\n");
    }
}

static void inspect_evm_xattr(const char *filepath) {
    uint8_t buffer[512];
    ssize_t res = getxattr(filepath, "security.evm", buffer, sizeof(buffer));

    if (res < 0) {
        if (errno == ENODATA) {
            printf("[EVM] Атрибут security.evm відсутній\n");
        } else {
            perror("[EVM] Помилка системного виклику getxattr для security.evm");
        }
        return;
    }

    uint8_t type = buffer[0];
    printf("[EVM] Зчитано %zd байт. Тип метаданих: 0x%02x ", res, type);
    if (type == 0x03) {
        printf("(Симетричний HMAC над inode та xattrs)\n");
    } else if (type == 0x04) {
        printf("(Асиметричний Portable підпис метаданих)\n");
    } else {
        printf("(Невідомий тип атрибута EVM)\n");
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    printf("=== Аналіз цілісності файлу: %s ===\n", argv[1]);
    inspect_ima_xattr(argv[1]);
    inspect_evm_xattr(argv[1]);

    return EXIT_SUCCESS;
}
