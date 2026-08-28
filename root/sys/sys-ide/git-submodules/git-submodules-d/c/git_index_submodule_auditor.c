/* git_index_submodule_auditor.c — Прямий двійковий парсер .git/index та .gitmodules на C99 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <ctype.h>

#define DIRC_MAGIC 0x44495243
#define MODE_GITLINK 0160000

typedef struct {
    char path[1024];
    char url[2048];
    char index_sha[41];
    char head_sha[41];
    bool in_gitmodules;
    bool in_index;
    bool is_clean;
} submodule_audit_record_t;

typedef struct {
    submodule_audit_record_t *records;
    size_t count;
    size_t capacity;
} audit_table_t;

static uint32_t read_be32(const uint8_t *buf) {
    return ((uint32_t)buf[0] << 24) |
           ((uint32_t)buf[1] << 16) |
           ((uint32_t)buf[2] << 8)  |
           ((uint32_t)buf[3]);
}

static void sha_to_hex(const uint8_t *sha, char *out) {
    static const char hex[] = "0123456789abcdef";
    for (int i = 0; i < 20; i++) {
        out[i * 2]     = hex[(sha[i] >> 4) & 0x0F];
        out[i * 2 + 1] = hex[sha[i] & 0x0F];
    }
    out[40] = '\0';
}

static char *trim_str(char *s) {
    while (isspace((unsigned char)*s)) s++;
    if (*s == 0) return s;
    char *end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return s;
}

bool audit_table_init(audit_table_t *table) {
    table->capacity = 16;
    table->count = 0;
    table->records = calloc(table->capacity, sizeof(submodule_audit_record_t));
    return table->records != NULL;
}

void audit_table_free(audit_table_t *table) {
    if (table->records) {
        free(table->records);
        table->records = NULL;
    }
    table->count = 0;
    table->capacity = 0;
}

submodule_audit_record_t *audit_table_find_or_add(audit_table_t *table, const char *path) {
    for (size_t i = 0; i < table->count; i++) {
        if (strcmp(table->records[i].path, path) == 0) {
            return &table->records[i];
        }
    }
    if (table->count >= table->capacity) {
        size_t new_cap = table->capacity * 2;
        submodule_audit_record_t *new_rec = realloc(table->records, new_cap * sizeof(submodule_audit_record_t));
        if (!new_rec) return NULL;
        table->records = new_rec;
        table->capacity = new_cap;
    }
    submodule_audit_record_t *rec = &table->records[table->count++];
    memset(rec, 0, sizeof(*rec));
    strncpy(rec->path, path, sizeof(rec->path) - 1);
    return rec;
}

bool scan_git_index(const char *index_file_path, audit_table_t *table) {
    FILE *f = fopen(index_file_path, "rb");
    if (!f) return false;

    uint8_t header[12];
    if (fread(header, 1, 12, f) != 12) {
        fclose(f);
        return false;
    }

    uint32_t magic = read_be32(header);
    uint32_t version = read_be32(header + 4);
    uint32_t num_entries = read_be32(header + 8);

    if (magic != DIRC_MAGIC || version < 2 || version > 4) {
        fclose(f);
        return false;
    }

    for (uint32_t i = 0; i < num_entries; i++) {
        uint8_t entry_fixed[62];
        if (fread(entry_fixed, 1, 62, f) != 62) break;

        uint32_t mode = read_be32(entry_fixed + 24);
        const uint8_t *sha = entry_fixed + 40;
        uint16_t flags = ((uint16_t)entry_fixed[60] << 8) | entry_fixed[61];
        uint16_t name_len = flags & 0x0FFF;

        char path_buf[1024];
        size_t path_bytes = 0;

        if (name_len < 0x0FFF) {
            if (fread(path_buf, 1, name_len, f) != name_len) break;
            path_buf[name_len] = '\0';
            path_bytes = name_len;
        } else {
            int c;
            while ((c = fgetc(f)) != EOF && c != '\0' && path_bytes < sizeof(path_buf) - 1) {
                path_buf[path_bytes++] = (char)c;
            }
            path_buf[path_bytes] = '\0';
        }

        /* Облік нульових байтів вирівнювання (8-байтова межа) */
        size_t total_len = 62 + path_bytes;
        size_t pad = 8 - (total_len % 8);
        if (pad == 0) pad = 8;
        for (size_t p = 0; p < pad; p++) fgetc(f);

        if ((mode & 0170000) == MODE_GITLINK) {
            submodule_audit_record_t *rec = audit_table_find_or_add(table, path_buf);
            if (rec) {
                sha_to_hex(sha, rec->index_sha);
                rec->in_index = true;
            }
        }
    }

    fclose(f);
    return true;
}

bool scan_gitmodules(const char *gitmodules_path, audit_table_t *table) {
    FILE *f = fopen(gitmodules_path, "r");
    if (!f) return false;

    char line_buf[4096];
    char current_path[1024] = {0};
    char current_url[2048] = {0};

    while (fgets(line_buf, sizeof(line_buf), f)) {
        char *line = trim_str(line_buf);
        if (line[0] == '\0' || line[0] == '#' || line[0] == ';') continue;

        if (line[0] == '[') {
            if (current_path[0] != '\0') {
                submodule_audit_record_t *rec = audit_table_find_or_add(table, current_path);
                if (rec) {
                    strncpy(rec->url, current_url, sizeof(rec->url) - 1);
                    rec->in_gitmodules = true;
                }
                current_path[0] = '\0';
                current_url[0] = '\0';
            }
            continue;
        }

        char *eq = strchr(line, '=');
        if (!eq) continue;
        *eq = '\0';
        char *k = trim_str(line);
        char *v = trim_str(eq + 1);

        if (strcmp(k, "path") == 0) {
            strncpy(current_path, v, sizeof(current_path) - 1);
        } else if (strcmp(k, "url") == 0) {
            strncpy(current_url, v, sizeof(current_url) - 1);
        }
    }

    if (current_path[0] != '\0') {
        submodule_audit_record_t *rec = audit_table_find_or_add(table, current_path);
        if (rec) {
            strncpy(rec->url, current_url, sizeof(rec->url) - 1);
            rec->in_gitmodules = true;
        }
    }

    fclose(f);
    return true;
}

void verify_head_states(const char *repo_root, audit_table_t *table) {
    char path_buf[2048];
    for (size_t i = 0; i < table->count; i++) {
        submodule_audit_record_t *rec = &table->records[i];
        snprintf(path_buf, sizeof(path_buf), "%s/.git/modules/%s/HEAD", repo_root, rec->path);

        FILE *f = fopen(path_buf, "r");
        if (f) {
            char head_buf[128];
            if (fgets(head_buf, sizeof(head_buf), f)) {
                char *trimmed = trim_str(head_buf);
                strncpy(rec->head_sha, trimmed, sizeof(rec->head_sha) - 1);
            }
            fclose(f);
        } else {
            strncpy(rec->head_sha, "MISSING_HEAD", sizeof(rec->head_sha) - 1);
        }

        rec->is_clean = (strcmp(rec->index_sha, rec->head_sha) == 0);
    }
}
