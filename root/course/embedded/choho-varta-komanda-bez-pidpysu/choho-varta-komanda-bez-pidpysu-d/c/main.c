/*
 * Стенд: чого коштує звіряти тег автентичності через memcmp.
 *
 * Збірка:  cc -O2 -std=c11 -o ctdemo *.c
 *
 * Один і той самий нападник працює проти двох приймачів, які відрізняються
 * РІВНО одним рядком — способом звіряння тегу.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "attack.h"
#include "ct.h"
#include "oracle.h"

/* Нібито тег HMAC-SHA256 законної команди «CMD_DISARM». */
static const uint8_t secret_tag[TAG_LEN] = {
    0x9f, 0x1c, 0x40, 0xa7, 0x33, 0xd8, 0x0b, 0x62,
    0x5e, 0xf4, 0x21, 0x8c, 0x77, 0x09, 0xba, 0xd3,
    0x46, 0xe1, 0x58, 0x2a, 0xc9, 0x70, 0x3f, 0x84,
    0x1d, 0xb6, 0x05, 0xef, 0x92, 0x6b, 0xa8, 0x37
};

static size_t matching_bytes(const uint8_t *a, const uint8_t *b)
{
    size_t i;
    size_t hits = 0;

    for (i = 0; i < TAG_LEN; ++i) {
        if (a[i] == b[i]) {
            hits++;
        }
    }
    return hits;
}

static void print_tag(const char *label, const uint8_t *tag)
{
    size_t i;

    printf("%s", label);
    for (i = 0; i < TAG_LEN; ++i) {
        printf("%02x", tag[i]);
    }
    printf("\n");
}

static attack_report run_case(const char *title, oracle_mode mode)
{
    oracle o;
    attack_report report;

    /* Той самий засів джитеру в обох дослідах: різницю дає спосіб
       звіряння, а не випадковість стенда. */
    oracle_init(&o, secret_tag, mode, 0x00c0ffeeu);
    report = attack_recover_tag(&o);
    oracle_destroy(&o);

    printf("--- %s ---\n", title);
    printf("  кадрів надіслано:      %llu\n", (unsigned long long)report.queries);
    printf("  байтів тегу вгадано:   %zu з %d\n",
           matching_bytes(report.tag, secret_tag), TAG_LEN);
    printf("  приймач прийняв кадр:  %s\n", report.accepted ? "ТАК" : "ні");
    print_tag("  зібраний тег:          ", report.tag);
    printf("\n");

    return report;
}

int main(void)
{
    attack_report naive;
    attack_report constant;

    print_tag("Секрет приймача (нападнику невідомий): ", secret_tag);
    printf("Повний перебір 32-байтного тегу коштував би 2^256 спроб.\n");
    printf("Побайтовий підбір — 32 * 256 = 8192 різних кадри;\n");
    printf("на живому стенді кожен доводиться повторити, щоб усереднити шум.\n\n");

    naive = run_case("Приймач звіряє тег через memcmp", ORACLE_NAIVE);
    constant = run_case("Приймач звіряє тег через ct_verify", ORACLE_CONSTANT_TIME);

    if (!naive.accepted) {
        fprintf(stderr, "стенд зламано: наївний приймач мав віддати тег\n");
        return EXIT_FAILURE;
    }
    if (constant.accepted) {
        fprintf(stderr, "стенд зламано: звіряння за сталий час не мало піддатися\n");
        return EXIT_FAILURE;
    }

    printf("Різниця в коді — один виклик. Різниця в наслідках — уся система.\n");
    return EXIT_SUCCESS;
}
