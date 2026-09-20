#include "cli_adapter.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#if defined(_MSC_VER) && !defined(__MINGW32__)
/* Лаконічна заміна getopt_long для компіляторів MSVC без зовнішніх залежностей */
static int optind = 1;
static char *optarg = NULL;

struct option {
    const char *name;
    int has_arg;
    int *flag;
    int val;
};
#define no_argument 0
#define required_argument 1

static int getopt_long(int argc, char *const argv[], const char *optstring,
                       const struct option *longopts, int *longindex) {
    (void)optstring;
    (void)longindex;
    if (optind >= argc) return -1;
    char *arg = argv[optind];
    if (arg[0] != '-') return -1;

    optarg = NULL;
    if (arg[1] == '-') {
        const char *opt_name = &arg[2];
        for (int i = 0; longopts[i].name != NULL; i++) {
            if (strcmp(opt_name, longopts[i].name) == 0) {
                optind++;
                if (longopts[i].has_arg == required_argument) {
                    if (optind < argc) {
                        optarg = argv[optind++];
                    } else {
                        return '?';
                    }
                }
                return longopts[i].val;
            }
        }
        optind++;
        return '?';
    } else {
        char c = arg[1];
        optind++;
        for (int i = 0; longopts[i].name != NULL; i++) {
            if (longopts[i].val == c) {
                if (longopts[i].has_arg == required_argument) {
                    if (optind < argc) {
                        optarg = argv[optind++];
                    } else {
                        return '?';
                    }
                }
                return c;
            }
        }
        return '?';
    }
}
#else
#include <getopt.h>
#endif

/**
 * @file cli_adapter.c
 * @brief Реалізація драйвуючого адаптера CLI на базі getopt_long.
 */

int cli_adapter_run(inbound_port_t *port, int argc, char **argv) {
    if (!port) {
        fprintf(stderr, "[CLI] Помилка: відсутній зв'язок із вхідним портом ядра\n");
        return CLI_EXIT_INTERNAL_ERROR;
    }

    /* Скидання глобального стану парсера для повторних викликів у межах одного процесу */
    optind = 1;
#if !defined(_MSC_VER) || defined(__MINGW32__)
    opterr = 0;
#endif

    char room_id[CLIMATE_ROOM_ID_LEN] = {0};
    char auth_token[CLIMATE_AUTH_TOKEN_LEN] = {0};
    double target_temp = 0.0;
    bool has_room = false;
    bool has_temp = false;
    bool has_token = false;

    static const struct option options[] = {
        {"room",  required_argument, NULL, 'r'},
        {"temp",  required_argument, NULL, 't'},
        {"token", required_argument, NULL, 'k'},
        {"help",  no_argument,       NULL, 'h'},
        {NULL,    0,                 NULL,  0 }
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "r:t:k:h", options, NULL)) != -1) {
        switch (opt) {
            case 'r':
                strncpy(room_id, optarg, sizeof(room_id) - 1);
                has_room = true;
                break;
            case 't': {
                char *endptr = NULL;
                target_temp = strtod(optarg, &endptr);
                if (endptr == optarg || *endptr != '\0') {
                    fprintf(stderr, "[CLI] Помилка синтаксису: значення температури '%s' не є дійсним числом\n", optarg);
                    return CLI_EXIT_INVALID_SYNTAX;
                }
                has_temp = true;
                break;
            }
            case 'k':
                strncpy(auth_token, optarg, sizeof(auth_token) - 1);
                has_token = true;
                break;
            case 'h':
                printf("Використання: %s --room <кімната> --temp <температура> --token <токен>\n", argv[0]);
                return CLI_EXIT_SUCCESS;
            default:
                fprintf(stderr, "[CLI] Помилка синтаксису: невідомий прапорець командного рядка\n");
                return CLI_EXIT_INVALID_SYNTAX;
        }
    }

    /* Перевірка наявності всіх необхідних параметрів */
    if (!has_room || !has_temp || !has_token) {
        fprintf(stderr, "[CLI] Помилка синтаксису: обов'язкові параметри (--room, --temp, --token) відсутні\n");
        return CLI_EXIT_INVALID_SYNTAX;
    }

    /* Трансляція консольних параметрів у нейтральну команду вхідного порту */
    climate_cmd_t cmd;
    memset(&cmd, 0, sizeof(cmd));
    strncpy(cmd.room_id, room_id, sizeof(cmd.room_id) - 1);
    cmd.target_temp_c = target_temp;
    strncpy(cmd.auth_token, auth_token, sizeof(cmd.auth_token) - 1);

    climate_result_t result;
    memset(&result, 0, sizeof(result));

    core_status_t status = inbound_port_execute(port, &cmd, &result);

    /* Трансляція доменного статусу ядра у вихідний системний код процесу */
    switch (status) {
        case CORE_STATUS_OK:
            printf("[CLI] Успіх (код %d): %s\n", CLI_EXIT_SUCCESS, result.message);
            return CLI_EXIT_SUCCESS;

        case CORE_STATUS_INVALID_ARG:
            fprintf(stderr, "[CLI] Помилка аргументу ядра (код %d): %s\n", CLI_EXIT_INVALID_ARG, result.message);
            return CLI_EXIT_INVALID_ARG;

        case CORE_STATUS_UNAUTHORIZED:
            fprintf(stderr, "[CLI] Помилка авторизації (код %d): %s\n", CLI_EXIT_UNAUTHORIZED, result.message);
            return CLI_EXIT_UNAUTHORIZED;

        case CORE_STATUS_OUT_OF_RANGE:
            fprintf(stderr, "[CLI] Температура поза діапазоном (код %d): %s\n", CLI_EXIT_OUT_OF_RANGE, result.message);
            return CLI_EXIT_OUT_OF_RANGE;

        case CORE_STATUS_INTERNAL_ERROR:
        default:
            fprintf(stderr, "[CLI] Системна помилка ядра (код %d): %s\n", CLI_EXIT_INTERNAL_ERROR, result.message);
            return CLI_EXIT_INTERNAL_ERROR;
    }
}
