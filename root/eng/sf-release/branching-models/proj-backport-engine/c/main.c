#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_SHA_LEN 64
#define MAX_LINE_LEN 1024
#define MAX_FILES 128

typedef enum {
    BACKPORT_OK = 0,
    BACKPORT_ERR_NO_UPSTREAM = 1,
    BACKPORT_ERR_INVALID_HEADER = 2,
    BACKPORT_ERR_DIFF_TOO_LARGE = 3
} backport_status_t;

typedef struct {
    char target_branch[32];
    char upstream_sha[MAX_SHA_LEN];
    char commit_subject[MAX_LINE_LEN];
    int lines_added;
    int lines_deleted;
    int files_changed_count;
    char changed_files[MAX_FILES][128];
} backport_metadata_t;

static void trim_trailing_newline(char *str) {
    size_t len = strlen(str);
    while (len > 0 && (str[len - 1] == '\n' || str[len - 1] == '\r')) {
        str[--len] = '\0';
    }
}

static bool extract_upstream_sha(const char *line, char *out_sha, size_t max_out) {
    const char *pattern_cp = "(cherry picked from commit ";
    const char *pattern_up = "Upstream-commit: ";
    const char *pos = strstr(line, pattern_cp);
    
    if (pos) {
        pos += strlen(pattern_cp);
        size_t idx = 0;
        while (*pos && *pos != ')' && idx < max_out - 1) {
            out_sha[idx++] = *pos++;
        }
        out_sha[idx] = '\0';
        return idx >= 7; /* Мінімальна довжина скороченого SHA */
    }

    pos = strstr(line, pattern_up);
    if (pos) {
        pos += strlen(pattern_up);
        size_t idx = 0;
        while (*pos && *pos != ' ' && *pos != '\n' && *pos != '\r' && idx < max_out - 1) {
            out_sha[idx++] = *pos++;
        }
        out_sha[idx] = '\0';
        return idx >= 7;
    }

    return false;
}

backport_status_t validate_backport_stream(FILE *stream, backport_metadata_t *meta) {
    char line_buf[MAX_LINE_LEN];
    bool has_header = false;
    bool found_upstream = false;

    memset(meta, 0, sizeof(*meta));

    while (fgets(line_buf, sizeof(line_buf), stream)) {
        trim_trailing_newline(line_buf);

        /* Перевірка першого рядка: заголовок коміту */
        if (!has_header && strlen(line_buf) > 0) {
            strncpy(meta->commit_subject, line_buf, sizeof(meta->commit_subject) - 1);
            has_header = true;

            /* Перевірка префікса гілки [vX.Y] */
            if (line_buf[0] == '[' && strchr(line_buf, ']')) {
                const char *end_bracket = strchr(line_buf, ']');
                size_t b_len = (size_t)(end_bracket - line_buf - 1);
                if (b_len < sizeof(meta->target_branch)) {
                    strncpy(meta->target_branch, line_buf + 1, b_len);
                    meta->target_branch[b_len] = '\0';
                }
            }
            continue;
        }

        /* Пошук мітки Upstream SHA */
        if (!found_upstream && extract_upstream_sha(line_buf, meta->upstream_sha, sizeof(meta->upstream_sha))) {
            found_upstream = true;
        }

        /* Парсинг рядків статистики diffstat: ' 3 files changed, 10 insertions(+), 2 deletions(-)' */
        if (strstr(line_buf, "files changed") || strstr(line_buf, "file changed")) {
            int fc = 0;
            if (sscanf(line_buf, " %d file", &fc) == 1) {
                meta->files_changed_count = fc;
            }
            char *p_ins = strstr(line_buf, "insertion");
            if (p_ins) {
                char *rev = p_ins - 2;
                while (rev > line_buf && *rev != ' ' && *rev != ',') rev--;
                meta->lines_added = atoi(rev + 1);
            }
            char *p_del = strstr(line_buf, "deletion");
            if (p_del) {
                char *rev = p_del - 2;
                while (rev > line_buf && *rev != ' ' && *rev != ',') rev--;
                meta->lines_deleted = atoi(rev + 1);
            }
        }
    }

    if (!found_upstream) {
        return BACKPORT_ERR_NO_UPSTREAM;
    }

    if (meta->lines_added + meta->lines_deleted > 300) {
        return BACKPORT_ERR_DIFF_TOO_LARGE;
    }

    return BACKPORT_OK;
}

int main(void) {
    const char *sample_log =
        "[v2.4] fix(io): prevent file descriptor leak during ring reset\n"
        "\n"
        "Under high packet rates, resetting the descriptor ring failed to close\n"
        "pending eventfds, leading to exhaustion of process handles.\n"
        "\n"
        "(cherry picked from commit 8f4a21b3c990a174f82d1c9b3a0e4123456789ab)\n"
        "Fixes: CVE-2026-1940\n"
        "---\n"
        " 2 files changed, 14 insertions(+), 3 deletions(-)\n";

    FILE *input = fmemopen((void *)sample_log, strlen(sample_log), "r");
    if (!input) {
        perror("fmemopen failed");
        return EXIT_FAILURE;
    }

    backport_metadata_t meta;
    backport_status_t res = validate_backport_stream(input, &meta);
    fclose(input);

    if (res == BACKPORT_OK) {
        printf("STATUS: VALID BACKPORT\n");
        printf("Target Branch : %s\n", meta.target_branch);
        printf("Upstream SHA  : %s\n", meta.upstream_sha);
        printf("Delta Lines   : +%d / -%d\n", meta.lines_added, meta.lines_deleted);
    } else {
        printf("STATUS: REJECTED (code %d)\n", res);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
