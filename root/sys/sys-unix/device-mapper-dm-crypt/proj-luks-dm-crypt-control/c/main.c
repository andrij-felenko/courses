#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libcryptsetup.h>

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <пристрій> <ім'я_відображення> <пароль>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *device_path = argv[1];
    const char *target_name = argv[2];
    const char *passphrase = argv[3];

    struct crypt_device *cd = NULL;
    int r;

    /* 1. Ініціалізація контексту для блокового пристрою */
    r = crypt_init(&cd, device_path);
    if (r < 0) {
        fprintf(stderr, "Помилка crypt_init для %s: %s\n", device_path, strerror(-r));
        return EXIT_FAILURE;
    }

    /* 2. Зчитування та валідація заголовка LUKS */
    r = crypt_load(cd, CRYPT_LUKS, NULL);
    if (r < 0) {
        fprintf(stderr, "Помилка зчитування заголовка LUKS на %s: %s\n", device_path, strerror(-r));
        crypt_free(cd);
        return EXIT_FAILURE;
    }

    printf("Успішно зчитано заголовок!\n");
    printf("Тип заголовка: %s\n", crypt_get_type(cd));
    printf("UUID тома:     %s\n", crypt_get_uuid(cd));

    /* 3. Активація зашифрованого тома парольною фразою */
    r = crypt_activate_by_passphrase(cd, target_name, CRYPT_ANY_SLOT,
                                     passphrase, strlen(passphrase), 0);
    if (r < 0) {
        fprintf(stderr, "Помилка аутентифікації або активації: %s\n", strerror(-r));
        crypt_free(cd);
        return EXIT_FAILURE;
    }

    printf("Пристрій успішно активовано: /dev/mapper/%s (використано слот ключа %d)\n", target_name, r);

    /* 4. Безумовне звільнення ресурсів контексту */
    crypt_free(cd);
    return EXIT_SUCCESS;
}
