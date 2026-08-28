#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура запиту на виділення підмережі */
typedef struct {
    char name[64];
    uint32_t required_hosts;
    bool is_p2p_31;
    uint32_t allocated_size;
    uint8_t prefix_len;
    uint32_t net_ip;
    uint32_t mask;
    uint32_t first_host;
    uint32_t last_host;
    uint32_t broadcast_ip;
} Subnet;

/* Перетворення рядка IPv4 у 32-бітне число в host byte order */
bool parse_ipv4(const char *str, uint32_t *out_ip) {
    unsigned int b3, b2, b1, b0;
    if (sscanf(str, "%u.%u.%u.%u", &b3, &b2, &b1, &b0) != 4) return false;
    if (b3 > 255 || b2 > 255 || b1 > 255 || b0 > 255) return false;
    *out_ip = ((uint32_t)b3 << 24) | ((uint32_t)b2 << 16) | ((uint32_t)b1 << 8) | (uint32_t)b0;
    return true;
}

/* Форматування 32-бітного числа в рядок IPv4 */
void format_ipv4(uint32_t ip, char *buf, size_t len) {
    snprintf(buf, len, "%u.%u.%u.%u",
             (ip >> 24) & 0xFF, (ip >> 16) & 0xFF,
             (ip >> 8) & 0xFF, ip & 0xFF);
}

/* Обчислення найменшого степеня двійки 2^h >= val */
uint8_t compute_host_bits(uint32_t val) {
    uint8_t bits = 0;
    uint32_t size = 1;
    while (size < val && bits < 32) {
        size <<= 1;
        bits++;
    }
    return bits;
}

/* Компаратор для сортування за спаданням виділеного розміру */
int compare_subnets_desc(const void *a, const void *b) {
    const Subnet *sa = (const Subnet *)a;
    const Subnet *sb = (const Subnet *)b;
    if (sa->allocated_size < sb->allocated_size) return 1;
    if (sa->allocated_size > sb->allocated_size) return -1;
    return 0;
}

/* Головна функція планування VLSM */
bool plan_vlsm(uint32_t root_ip, uint8_t root_prefix, Subnet *subnets, size_t count) {
    uint32_t root_size = (root_prefix == 0) ? 0xFFFFFFFF : (1U << (32 - root_prefix));
    uint32_t pool_start = root_ip & ~((root_prefix == 32) ? 0 : (root_size - 1));
    uint32_t pool_end = pool_start + root_size - 1;

    /* Крок 1: Обчислення розміру та маски для кожного запиту */
    for (size_t i = 0; i < count; i++) {
        if (subnets[i].is_p2p_31 && subnets[i].required_hosts == 2) {
            subnets[i].prefix_len = 31;
            subnets[i].allocated_size = 2;
        } else {
            uint32_t needed = subnets[i].required_hosts + 2; /* + мережа і broadcast */
            uint8_t h = compute_host_bits(needed);
            subnets[i].prefix_len = 32 - h;
            subnets[i].allocated_size = 1U << h;
        }
        subnets[i].mask = (subnets[i].prefix_len == 0) ? 0 : (~0U << (32 - subnets[i].prefix_len));
    }

    /* Крок 2: Сортування за спаданням розміру */
    qsort(subnets, count, sizeof(Subnet), compare_subnets_desc);

    /* Крок 3: Жадібне виділення адрес */
    uint32_t current_ip = pool_start;
    for (size_t i = 0; i < count; i++) {
        uint32_t sz = subnets[i].allocated_size;
        /* Вирівнювання адреси за межею блоку */
        current_ip = (current_ip + sz - 1) & ~(sz - 1);

        /* Перевірка виходу за межі пулу */
        if (current_ip > pool_end || (current_ip + sz - 1) > pool_end) {
            fprintf(stderr, "Помилка: пул вичерпано на підмережі '%s'!\n", subnets[i].name);
            return false;
        }

        subnets[i].net_ip = current_ip;
        if (subnets[i].prefix_len == 31) {
            subnets[i].first_host = current_ip;
            subnets[i].last_host = current_ip + 1;
            subnets[i].broadcast_ip = 0; /* Broadcast відсутній у /31 */
        } else {
            subnets[i].first_host = current_ip + 1;
            subnets[i].last_host = current_ip + sz - 2;
            subnets[i].broadcast_ip = current_ip + sz - 1;
        }

        current_ip += sz;
    }
    return true;
}

int main(void) {
    uint32_t root_ip;
    if (!parse_ipv4("10.100.0.0", &root_ip)) return 1;
    uint8_t root_prefix = 18;

    Subnet list[] = {
        { .name = "Server Farm",     .required_hosts = 500,  .is_p2p_31 = false },
        { .name = "Engineering Dept",.required_hosts = 220,  .is_p2p_31 = false },
        { .name = "Sales Dept",      .required_hosts = 120,  .is_p2p_31 = false },
        { .name = "Guest Wi-Fi",     .required_hosts = 1000, .is_p2p_31 = false },
        { .name = "Core Link A-B",   .required_hosts = 2,    .is_p2p_31 = true  },
        { .name = "Core Link B-C",   .required_hosts = 2,    .is_p2p_31 = true  }
    };
    size_t count = sizeof(list) / sizeof(list[0]);

    if (!plan_vlsm(root_ip, root_prefix, list, count)) return 1;

    printf("Результати планування VLSM для пулу 10.100.0.0/18:\n");
    printf("%-18s %-6s %-16s %-16s %-33s %-16s\n",
           "Підмережа", "Префікс", "Мережа", "Маска", "Діапазон хостів", "Broadcast");
    printf("----------------------------------------------------------------------------------------------------------------\n");

    char net_str[16], mask_str[16], first_str[16], last_str[16], brd_str[16], range_str[36];
    for (size_t i = 0; i < count; i++) {
        format_ipv4(list[i].net_ip, net_str, sizeof(net_str));
        format_ipv4(list[i].mask, mask_str, sizeof(mask_str));
        format_ipv4(list[i].first_host, first_str, sizeof(first_str));
        format_ipv4(list[i].last_host, last_str, sizeof(last_str));
        snprintf(range_str, sizeof(range_str), "%s - %s", first_str, last_str);

        if (list[i].prefix_len == 31) {
            snprintf(brd_str, sizeof(brd_str), "N/A (RFC 3021)");
        } else {
            format_ipv4(list[i].broadcast_ip, brd_str, sizeof(brd_str));
        }

        printf("%-18s /%-5u %-16s %-16s %-33s %-16s\n",
               list[i].name, list[i].prefix_len, net_str, mask_str, range_str, brd_str);
    }
    return 0;
}
