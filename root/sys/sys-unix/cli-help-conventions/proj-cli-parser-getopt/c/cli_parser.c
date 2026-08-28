/* cli_parser.c — реалізація на C з використанням POSIX/GNU getopt_long */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <stdbool.h>

#define PROGRAM_NAME "fileproc"
#define PROGRAM_VERSION "1.4.0"

typedef struct {
    bool verbose;
    bool quiet;
    const char *output_file;
    size_t buffer_size;
    const char *color_mode;
    char **input_files;
    int input_file_count;
} Config;

static void print_version(FILE *out) {
    fprintf(out, "%s version %s\n", PROGRAM_NAME, PROGRAM_VERSION);
    fprintf(out, "Copyright (C) 2026 Open Systems Foundation.\n");
    fprintf(out, "License: MIT (free and open source software).\n");
}

static void print_help(FILE *out) {
    fprintf(out, "Usage: %s [OPTION]... [FILE]...\n", PROGRAM_NAME);
    fprintf(out, "Process input files with customizable buffering and formatting.\n\n");

    fprintf(out, "Main operation mode:\n");
    fprintf(out, "  -o, --output=FILE       write processed data to FILE [default: stdout]\n");
    fprintf(out, "  -b, --buffer=BYTES      set processing buffer size in bytes [default: 4096]\n");
    fprintf(out, "      --color[=WHEN]      colorize console output; WHEN can be 'always',\n");
    fprintf(out, "                            'never', or 'auto' [default: auto]\n\n");

    fprintf(out, "Diagnostic and verbosity options:\n");
    fprintf(out, "  -v, --verbose           print detailed processing diagnostics\n");
    fprintf(out, "  -q, --quiet             suppress all warning and diagnostic messages\n\n");

    fprintf(out, "Informational options:\n");
    fprintf(out, "  -h, --help              display this help and exit\n");
    fprintf(out, "  -V, --version           output version information and exit\n\n");

    fprintf(out, "With no FILE, or when FILE is -, read standard input.\n");
    fprintf(out, "Exit status: 0 if OK, 1 if minor problems, 2 if serious trouble / invalid syntax.\n");
}

static bool parse_cli_options(int argc, char *argv[], Config *cfg) {
    /* Очищення структури за замовчуванням */
    cfg->verbose = false;
    cfg->quiet = false;
    cfg->output_file = NULL;
    cfg->buffer_size = 4096;
    cfg->color_mode = "auto";
    cfg->input_files = NULL;
    cfg->input_file_count = 0;

    static const char *short_opts = "o:b:vqhV";
    static const struct option long_opts[] = {
        {"output",   required_argument, NULL, 'o'},
        {"buffer",   required_argument, NULL, 'b'},
        {"color",    optional_argument, NULL, 'c'},
        {"verbose",  no_argument,       NULL, 'v'},
        {"quiet",    no_argument,       NULL, 'q'},
        {"help",     no_argument,       NULL, 'h'},
        {"version",  no_argument,       NULL, 'V'},
        {NULL, 0, NULL, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, short_opts, long_opts, NULL)) != -1) {
        switch (opt) {
            case 'o':
                cfg->output_file = optarg;
                break;
            case 'b': {
                char *endptr = NULL;
                long val = strtol(optarg, &endptr, 10);
                if (*endptr != '\0' || val <= 0) {
                    fprintf(stderr, "%s: invalid buffer size '%s'\n", PROGRAM_NAME, optarg);
                    fprintf(stderr, "Try '%s --help' for more information.\n", PROGRAM_NAME);
                    exit(2);
                }
                cfg->buffer_size = (size_t)val;
                break;
            }
            case 'c':
                if (optarg) {
                    if (strcmp(optarg, "always") != 0 &&
                        strcmp(optarg, "never") != 0 &&
                        strcmp(optarg, "auto") != 0) {
                        fprintf(stderr, "%s: unrecognized color mode '%s'\n", PROGRAM_NAME, optarg);
                        fprintf(stderr, "Try '%s --help' for more information.\n", PROGRAM_NAME);
                        exit(2);
                    }
                    cfg->color_mode = optarg;
                } else {
                    cfg->color_mode = "always";
                }
                break;
            case 'v':
                cfg->verbose = true;
                break;
            case 'q':
                cfg->quiet = true;
                break;
            case 'h':
                print_help(stdout);
                exit(0);
            case 'V':
                print_version(stdout);
                exit(0);
            case '?':
            default:
                /* getopt_long сам друкує опис невідомої опції у stderr */
                fprintf(stderr, "Try '%s --help' for more information.\n", PROGRAM_NAME);
                exit(2);
        }
    }

    if (cfg->verbose && cfg->quiet) {
        fprintf(stderr, "%s: options --verbose and --quiet are mutually exclusive\n", PROGRAM_NAME);
        exit(2);
    }

    /* Усі елементи argv після optind — позиційні операнди (імена файлів) */
    cfg->input_file_count = argc - optind;
    if (cfg->input_file_count > 0) {
        cfg->input_files = &argv[optind];
    }

    return true;
}

int main(int argc, char *argv[]) {
    Config cfg;
    parse_cli_options(argc, argv, &cfg);

    if (cfg.verbose) {
        printf("[DEBUG] Буфер: %zu байт, Колір: %s, Вивід: %s\n",
               cfg.buffer_size, cfg.color_mode,
               cfg.output_file ? cfg.output_file : "<stdout>");
        printf("[DEBUG] Вхідних файлів для обробки: %d\n", cfg.input_file_count);
    }

    /* Якщо файлів не передано, обробляємо стандартний ввід */
    if (cfg.input_file_count == 0) {
        if (!cfg.quiet) printf("Читання даних зі стандартного вводу (stdin)...\n");
    } else {
        for (int i = 0; i < cfg.input_file_count; ++i) {
            if (!cfg.quiet) printf("Обробка файлу: %s\n", cfg.input_files[i]);
        }
    }

    return 0;
}
