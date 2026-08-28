/* libnss_custom.c — C реалізація NSS модуля для розв'язання .lab доменів */
#define _GNU_SOURCE
#include <nss.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>
#include <arpa/inet.h>
#include <stdint.h>

#define LAB_SUFFIX ".lab"
#define SYNTHETIC_IP "127.0.42.1"

enum nss_status _nss_custom_gethostbyname2_r(
    const char *name,
    int af,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop)
{
    /* Модуль обробляє виключно IPv4 адреси (AF_INET) */
    if (af != AF_INET || name == NULL) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    /* Перевіряємо, чи має ім'я хоста локальний суфікс .lab */
    size_t name_len = strlen(name);
    size_t suffix_len = strlen(LAB_SUFFIX);
    if (name_len < suffix_len || strcmp(name + name_len - suffix_len, LAB_SUFFIX) != 0) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    /* Обчислюємо точні розміри всіх елементів, які будуть поміщені в буфер */
    size_t name_bytes = name_len + 1;
    size_t addr_bytes = sizeof(struct in_addr);
    size_t addr_list_bytes = 2 * sizeof(char *);
    size_t alias_list_bytes = 1 * sizeof(char *);

    /* Перевіряємо зальний необхідний обсяг з урахуванням вирівнювання */
    size_t total_needed = name_bytes + addr_bytes + addr_list_bytes + alias_list_bytes + 32;
    if (buflen < total_needed) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }

    /* Розміщуємо фрагменти даних у наданому буфері пам'яті */
    char *p = buffer;

    /* 1. Копіюємо текстове ім'я хоста */
    char *h_name = p;
    memcpy(h_name, name, name_bytes);
    p += name_bytes;

    /* Вирівнюємо поточний вказівник до межі sizeof(void *) для запобігання SIGBUS */
    uintptr_t pad = (uintptr_t)p % sizeof(void *);
    if (pad != 0) {
        p += (sizeof(void *) - pad);
    }

    /* 2. Записуємо двійкову структуру IPv4 адреси */
    struct in_addr *addr_ptr = (struct in_addr *)p;
    p += addr_bytes;
    if (inet_pton(AF_INET, SYNTHETIC_IP, addr_ptr) <= 0) {
        *errnop = EINVAL;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_UNAVAIL;
    }

    /* Вирівнюємо вказівник перед записом масивів вказівників */
    pad = (uintptr_t)p % sizeof(void *);
    if (pad != 0) {
        p += (sizeof(void *) - pad);
    }

    /* 3. Формуємо масив вказівників на IP адреси h_addr_list */
    char **h_addr_list = (char **)p;
    p += addr_list_bytes;
    h_addr_list[0] = (char *)addr_ptr;
    h_addr_list[1] = NULL;

    /* 4. Формуємо порожній масив псевдонімів h_aliases */
    char **h_aliases = (char **)p;
    h_aliases[0] = NULL;

    /* Заповнюємо вихідну структуру hostent вказівниками з наданого буфера */
    result->h_name = h_name;
    result->h_aliases = h_aliases;
    result->h_addrtype = AF_INET;
    result->h_length = sizeof(struct in_addr);
    result->h_addr_list = h_addr_list;

    *h_errnop = NETDB_SUCCESS;
    return NSS_STATUS_SUCCESS;
}

enum nss_status _nss_custom_gethostbyname_r(
    const char *name,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop)
{
    return _nss_custom_gethostbyname2_r(name, AF_INET, result, buffer, buflen, errnop, h_errnop);
}
