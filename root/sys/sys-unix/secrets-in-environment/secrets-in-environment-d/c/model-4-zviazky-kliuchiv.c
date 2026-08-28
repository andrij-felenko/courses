/* Додавання та читання секрету з Process Keyring мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/keyctl.h>

/* Обертки для системних викликів керування ключами */
static inline key_serial_t sys_add_key(const char *type, const char *description,
                                       const void *payload, size_t plen,
                                       key_serial_t ringid) {
    return (key_serial_t)syscall(__NR_add_key, type, description, payload, plen, ringid);
}

static inline long sys_keyctl(int operation, unsigned long arg2, unsigned long arg3,
                              unsigned long arg4, unsigned long arg5) {
    return syscall(__NR_keyctl, operation, arg2, arg3, arg4, arg5);
}

int main(void) {
    const char secret_value[] = "MasterKey_Crypto_2026";
    
    /* Зберігаємо секрет у зв'язці процесу (Process Keyring) */
    key_serial_t key = sys_add_key("user", "db_master_pass",
                                   secret_value, sizeof(secret_value),
                                   KEY_SPEC_PROCESS_KEYRING);
    if (key < 0) {
        perror("add_key");
        return EXIT_FAILURE;
    }
    printf("Ключ збережено в ядрі з дескриптором ID: %d\n", key);

    /* Встановлюємо таймаут життя ключа: 300 секунд (5 хвилин) */
    if (sys_keyctl(KEYCTL_SET_TIMEOUT, key, 300, 0, 0) < 0) {
        perror("keyctl SET_TIMEOUT");
    }

    /* Читання секрету з ядра */
    char buffer[128];
    long len = sys_keyctl(KEYCTL_READ, key, (unsigned long)buffer, sizeof(buffer), 0);
    if (len > 0) {
        printf("Зчитано секрет із ядра: %.*s\n", (int)len, buffer);
        /* Безпечне занулення буфера користувача */
        explicit_bzero(buffer, sizeof(buffer));
    }

    return EXIT_SUCCESS;
}
