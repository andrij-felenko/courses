/* submodule_tree_auditor.c — Повноцінний аудитор підмодулів та ліцензій на C99 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <ctype.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define DIRC_MAGIC 0x44495243
#define MODE_GITLINK 0160000
#define MAX_RECURSION_DEPTH 16

typedef enum {
    STATUS_OK = 0,
    STATUS_UNINITIALIZED = 1,
    STATUS_COMMIT_DRIFT = 2,
    STATUS_INSECURE_URL = 3,
    STATUS_CONFIG_MISMATCH = 4
} audit_status_t;

typedef enum {
    LICENSE_UNKNOWN = 0,
    LICENSE_PERMISSIVE = 1,
    LICENSE_WEAK_COPYLEFT = 2,
    LICENSE_STRONG_COPYLEFT = 3
} license_category_t;

typedef struct {
    char path[512];
    char url[1024];
    char index_sha[41];
    char head_sha[41];
    char detected_license[64];
    license_category_t license_cat;
    audit_status_t status;
    bool in_gitmodules;
    bool in_index;
    int depth;
} audit_record_t;

typedef struct {
    audit_record_t *records;
    size_t count;
    size_t capacity;
    char visited_paths[128][512];
    size_t visited_count;
} audit_engine_t;

static uint32_t read_be32(const uint8_t *b) {
    return ((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16) | ((uint32_t)b[2] << 8) | ((uint32_t)b[3]);
}

static void sha1_to_hex(const uint8_t *sha, char *out) {
    static const char hex[] = "0123456789abcdef";
    for (int i = 0; i < 20; i++) {
        out[i * 2]     = hex[(sha[i] >> 4) & 0x0F];
        out[i * 2 + 1] = hex[sha[i] & 0x0F];
    }
    out[40] = '\0';
}

static char *trim_whitespace(char *s) {
    while (isspace((unsigned char)*s)) s++;
    if (*s == 0) return s;
    char *end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return s;
}

bool engine_init(audit_engine_t *eng) {
    eng->capacity = 32;
    eng->count = 0;
    eng->visited_count = 0;
    eng->records = calloc(eng->capacity, sizeof(audit_record_t));
    return eng->records != NULL;
}

void engine_free(audit_engine_t *eng) {
    if (eng->records) free(eng->records);
    eng->records = NULL;
    eng->count = 0;
    eng->capacity = 0;
}

audit_record_t *engine_get_or_add(audit_engine_t *eng, const char *path, int depth) {
    for (size_t i = 0; i < eng->count; i++) {
        if (strcmp(eng->records[i].path, path) == 0) return &eng->records[i];
    }
    if (eng->count >= eng->capacity) {
        size_t new_cap = eng->capacity * 2;
        audit_record_t *new_recs = realloc(eng->records, new_cap * sizeof(audit_record_t));
        if (!new_recs) return NULL;
        eng->records = new_recs;
        eng->capacity = new_cap;
    }
    audit_record_t *r = &eng->records[eng->count++];
    memset(r, 0, sizeof(*r));
    strncpy(r->path, path, sizeof(r->path) - 1);
    strcpy(r->detected_license, "UNKNOWN");
    r->license_cat = LICENSE_UNKNOWN;
    r->depth = depth;
    return r;
}

license_category_t classify_spdx_license(const char *license) {
    if (strstr(license, "MIT") || strstr(license, "BSD") || strstr(license, "Apache") ||
        strstr(license, "ISC") || strstr(license, "Zlib") || strstr(license, "Unlicense") || strstr(license, "CC0")) {
        return LICENSE_PERMISSIVE;
    }
    if (strstr(license, "LGPL") || strstr(license, "MPL") || strstr(license, "CDDL") || strstr(license, "EPL")) {
        return LICENSE_WEAK_COPYLEFT;
    }
    if (strstr(license, "GPL") || strstr(license, "AGPL") || strstr(license, "SSPL")) {
        return LICENSE_STRONG_COPYLEFT;
    }
    return LICENSE_UNKNOWN;
}

void scan_spdx_in_file(const char *filepath, char *out_license, size_t max_len) {
    FILE *f = fopen(filepath, "r");
    if (!f) return;

    char line[512];
    int lines_count = 0;
    while (fgets(line, sizeof(line), f) && lines_count < 100) {
        lines_count++;
        char *spdx = strstr(line, "SPDX-License-Identifier:");
        if (spdx) {
            spdx += strlen("SPDX-License-Identifier:");
            char *trimmed = trim_whitespace(spdx);
            char *end_comment = strstr(trimmed, "*/");
            if (end_comment) *end_comment = '\0';
            trimmed = trim_whitespace(trimmed);
            if (strlen(trimmed) > 0) {
                strncpy(out_license, trimmed, max_len - 1);
                out_license[max_len - 1] = '\0';
                fclose(f);
                return;
            }
        }
    }
    fclose(f);
}

void scan_spdx_in_directory(const char *dir_path, char *out_license, size_t max_len) {
    DIR *d = opendir(dir_path);
    if (!d) return;

    struct dirent *entry;
    char sub_path[1024];

    while ((entry = readdir(d)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;
        if (strcmp(entry->d_name, ".git") == 0) continue;

        snprintf(sub_path, sizeof(sub_path), "%s/%s", dir_path, entry->d_name);
        struct stat st;
        if (stat(sub_path, &st) == -1) continue;

        if (S_ISDIR(st.st_mode)) {
            DIR *nested = opendir(sub_path);
            if (nested) {
                struct dirent *ne;
                while ((ne = readdir(nested)) != NULL) {
                    if (ne->d_name[0] == '.') continue;
                    char file_path[1024];
                    snprintf(file_path, sizeof(file_path), "%s/%s", sub_path, ne->d_name);
                    const char *ext = strrchr(ne->d_name, '.');
                    if (ext && (strcmp(ext, ".c") == 0 || strcmp(ext, ".h") == 0 || strcmp(ext, ".cpp") == 0 || strcmp(ext, ".hpp") == 0)) {
                        scan_spdx_in_file(file_path, out_license, max_len);
                        if (strcmp(out_license, "UNKNOWN") != 0) {
                            closedir(nested);
                            closedir(d);
                            return;
                        }
                    }
                }
                closedir(nested);
            }
        } else if (S_ISREG(st.st_mode)) {
            const char *ext = strrchr(entry->d_name, '.');
            if (ext && (strcmp(ext, ".c") == 0 || strcmp(ext, ".h") == 0 || strcmp(ext, ".cpp") == 0 || strcmp(ext, ".hpp") == 0 || strcmp(ext, ".S") == 0)) {
                scan_spdx_in_file(sub_path, out_license, max_len);
                if (strcmp(out_license, "UNKNOWN") != 0) {
                    closedir(d);
                    return;
                }
            } else if (strcasecmp(entry->d_name, "LICENSE") == 0 || strcasecmp(entry->d_name, "COPYING") == 0) {
                scan_spdx_in_file(sub_path, out_license, max_len);
                if (strcmp(out_license, "UNKNOWN") != 0) {
                    closedir(d);
                    return;
                }
            }
        }
    }
    closedir(d);
}

bool parse_binary_index(const char *index_path, audit_engine_t *eng, int depth, const char *prefix) {
    FILE *f = fopen(index_path, "rb");
    if (!f) return false;

    uint8_t hdr[12];
    if (fread(hdr, 1, 12, f) != 12) {
        fclose(f);
        return false;
    }

    uint32_t magic = read_be32(hdr);
    uint32_t version = read_be32(hdr + 4);
    uint32_t count = read_be32(hdr + 8);

    if (magic != DIRC_MAGIC || version < 2 || version > 4) {
        fclose(f);
        return false;
    }

    for (uint32_t i = 0; i < count; i++) {
        uint8_t fixed[62];
        if (fread(fixed, 1, 62, f) != 62) break;

        uint32_t mode = read_be32(fixed + 24);
        const uint8_t *sha = fixed + 40;
        uint16_t flags = ((uint16_t)fixed[60] << 8) | fixed[61];
        uint16_t name_len = flags & 0x0FFF;

        char path_buf[512];
        size_t bytes_read = 0;

        if (name_len < 0x0FFF) {
            if (fread(path_buf, 1, name_len, f) != name_len) break;
            path_buf[name_len] = '\0';
            bytes_read = name_len;
        } else {
            int c;
            while ((c = fgetc(f)) != EOF && c != '\0' && bytes_read < sizeof(path_buf) - 1) {
                path_buf[bytes_read++] = (char)c;
            }
            path_buf[bytes_read] = '\0';
        }

        size_t total = 62 + bytes_read;
        size_t pad = 8 - (total % 8);
        if (pad == 0) pad = 8;
        for (size_t p = 0; p < pad; p++) fgetc(f);

        if ((mode & 0170000) == MODE_GITLINK) {
            char full_path[512];
            if (prefix && strlen(prefix) > 0) {
                snprintf(full_path, sizeof(full_path), "%s/%s", prefix, path_buf);
            } else {
                strncpy(full_path, path_buf, sizeof(full_path) - 1);
            }

            audit_record_t *rec = engine_get_or_add(eng, full_path, depth);
            if (rec) {
                sha1_to_hex(sha, rec->index_sha);
                rec->in_index = true;
            }
        }
    }

    fclose(f);
    return true;
}

bool parse_gitmodules(const char *modules_path, audit_engine_t *eng, int depth, const char *prefix) {
    FILE *f = fopen(modules_path, "r");
    if (!f) return false;

    char line_buf[1024];
    char cur_path[512] = {0};
    char cur_url[1024] = {0};

    auto_flush:
    while (fgets(line_buf, sizeof(line_buf), f)) {
        char *line = trim_whitespace(line_buf);
        if (line[0] == '\0' || line[0] == '#' || line[0] == ';') continue;

        if (line[0] == '[') {
            if (cur_path[0] != '\0') {
                char full_path[512];
                if (prefix && strlen(prefix) > 0) {
                    snprintf(full_path, sizeof(full_path), "%s/%s", prefix, cur_path);
                } else {
                    strncpy(full_path, cur_path, sizeof(full_path) - 1);
                }

                audit_record_t *rec = engine_get_or_add(eng, full_path, depth);
                if (rec) {
                    strncpy(rec->url, cur_url, sizeof(rec->url) - 1);
                    rec->in_gitmodules = true;
                }
                cur_path[0] = '\0';
                cur_url[0] = '\0';
            }
            continue;
        }

        char *eq = strchr(line, '=');
        if (!eq) continue;
        *eq = '\0';
        char *k = trim_whitespace(line);
        char *v = trim_whitespace(eq + 1);

        if (strcmp(k, "path") == 0) {
            strncpy(cur_path, v, sizeof(cur_path) - 1);
        } else if (strcmp(k, "url") == 0) {
            strncpy(cur_url, v, sizeof(cur_url) - 1);
        }
    }

    if (cur_path[0] != '\0') {
        char full_path[512];
        if (prefix && strlen(prefix) > 0) {
            snprintf(full_path, sizeof(full_path), "%s/%s", prefix, cur_path);
        } else {
            strncpy(full_path, cur_path, sizeof(full_path) - 1);
        }

        audit_record_t *rec = engine_get_or_add(eng, full_path, depth);
        if (rec) {
            strncpy(rec->url, cur_url, sizeof(rec->url) - 1);
            rec->in_gitmodules = true;
        }
    }

    fclose(f);
    return true;
}

bool resolve_packed_ref(const char *packed_refs_path, const char *ref_name, char *out_sha, size_t max_len) {
    FILE *f = fopen(packed_refs_path, "r");
    if (!f) return false;

    char line[512];
    while (fgets(line, sizeof(line), f)) {
        char *trimmed = trim_whitespace(line);
        if (trimmed[0] == '#' || trimmed[0] == '^') continue;

        char *space = strchr(trimmed, ' ');
        if (!space) continue;

        *space = '\0';
        char *sha = trimmed;
        char *name = trim_whitespace(space + 1);

        if (strcmp(name, ref_name) == 0) {
            strncpy(out_sha, sha, max_len - 1);
            out_sha[max_len - 1] = '\0';
            fclose(f);
            return true;
        }
    }
    fclose(f);
    return false;
}

void audit_repository_recursive(const char *repo_root, const char *sub_prefix, int depth, audit_engine_t *eng) {
    if (depth > MAX_RECURSION_DEPTH) return;

    for (size_t i = 0; i < eng->visited_count; i++) {
        if (strcmp(eng->visited_paths[i], repo_root) == 0) return;
    }
    if (eng->visited_count < 128) {
        strncpy(eng->visited_paths[eng->visited_count++], repo_root, 511);
    }

    char index_path[1024];
    char modules_path[1024];
    snprintf(index_path, sizeof(index_path), "%s/.git/index", repo_root);
    snprintf(modules_path, sizeof(modules_path), "%s/.gitmodules", repo_root);

    parse_binary_index(index_path, eng, depth, sub_prefix);
    parse_gitmodules(modules_path, eng, depth, sub_prefix);

    char path_buf[1024];
    size_t current_count = eng->count;

    for (size_t i = 0; i < current_count; i++) {
        audit_record_t *rec = &eng->records[i];
        if (rec->depth != depth) continue;

        if (strncmp(rec->url, "http://", 7) == 0) {
            rec->status = STATUS_INSECURE_URL;
        }
        if (!rec->in_gitmodules || !rec->in_index) {
            rec->status = STATUS_CONFIG_MISMATCH;
        }

        snprintf(path_buf, sizeof(path_buf), "%s/.git/modules/%s/HEAD", repo_root, rec->path);
        FILE *f = fopen(path_buf, "r");
        if (f) {
            char head_buf[256];
            if (fgets(head_buf, sizeof(head_buf), f)) {
                char *trimmed = trim_whitespace(head_buf);
                if (strncmp(trimmed, "ref: ", 5) == 0) {
                    const char *ref_target = trimmed + 5;
                    char ref_file[1024];
                    snprintf(ref_file, sizeof(ref_file), "%s/.git/modules/%s/%s", repo_root, rec->path, ref_target);

                    FILE *rf = fopen(ref_file, "r");
                    if (rf) {
                        char rsha[128];
                        if (fgets(rsha, sizeof(rsha), rf)) {
                            strncpy(rec->head_sha, trim_whitespace(rsha), sizeof(rec->head_sha) - 1);
                        }
                        fclose(rf);
                    } else {
                        char packed_file[1024];
                        snprintf(packed_file, sizeof(packed_file), "%s/.git/modules/%s/packed-refs", repo_root, rec->path);
                        if (!resolve_packed_ref(packed_file, ref_target, rec->head_sha, sizeof(rec->head_sha))) {
                            strcpy(rec->head_sha, "UNKNOWN_REF");
                        }
                    }
                } else {
                    strncpy(rec->head_sha, trimmed, sizeof(rec->head_sha) - 1);
                }
            }
            fclose(f);
        } else {
            strcpy(rec->head_sha, "UNINITIALIZED");
            rec->status = STATUS_UNINITIALIZED;
        }

        if (rec->status == STATUS_OK && strcmp(rec->index_sha, rec->head_sha) != 0) {
            rec->status = STATUS_COMMIT_DRIFT;
        }

        snprintf(path_buf, sizeof(path_buf), "%s/%s", repo_root, rec->path);
        scan_spdx_in_directory(path_buf, rec->detected_license, sizeof(rec->detected_license));
        rec->license_cat = classify_spdx_license(rec->detected_license);

        char nested_gitmodules[1024];
        snprintf(nested_gitmodules, sizeof(nested_gitmodules), "%s/%s/.gitmodules", repo_root, rec->path);
        if (access(nested_gitmodules, F_OK) == 0) {
            char nested_root[1024];
            snprintf(nested_root, sizeof(nested_root), "%s/%s", repo_root, rec->path);
            audit_repository_recursive(nested_root, rec->path, depth + 1, eng);
        }
    }
}

void print_audit_table(const audit_engine_t *eng) {
    printf("\n================================= RECURSIVE SUBMODULE AUDIT REPORT =================================\n");
    printf("%-4s %-28s %-12s %-18s %-12s %s\n", "LVL", "SUBMODULE PATH", "STATUS", "SPDX LICENSE", "CATEGORY", "COMMIT DIVERGENCE (INDEX -> HEAD)");
    printf("----------------------------------------------------------------------------------------------------\n");

    for (size_t i = 0; i < eng->count; i++) {
        const audit_record_t *r = &eng->records[i];
        const char *st = "OK";
        if (r->status == STATUS_UNINITIALIZED) st = "UNINIT";
        else if (r->status == STATUS_COMMIT_DRIFT) st = "DRIFT";
        else if (r->status == STATUS_INSECURE_URL) st = "INSECURE";
        else if (r->status == STATUS_CONFIG_MISMATCH) st = "MISMATCH";

        const char *cat = "UNKNOWN";
        if (r->license_cat == LICENSE_PERMISSIVE) cat = "PERMISSIVE";
        else if (r->license_cat == LICENSE_WEAK_COPYLEFT) cat = "WEAK-COPY";
        else if (r->license_cat == LICENSE_STRONG_COPYLEFT) cat = "STRONG-COPY";

        char s_idx[9] = {0}, s_head[9] = {0};
        strncpy(s_idx, r->index_sha, 8);
        strncpy(s_head, r->head_sha, 8);

        printf("[%d]  %-28s %-12s %-18s %-12s %s -> %s\n",
               r->depth, r->path, st, r->detected_license, cat, s_idx, s_head);
    }
    printf("====================================================================================================\n\n");
}

void export_sbom_json(const char *out_path, const audit_engine_t *eng) {
    FILE *f = fopen(out_path, "w");
    if (!f) return;

    fprintf(f, "{\n");
    fprintf(f, "  \"$schema\": \"https://cyclonedx.org/schema/bom-1.5.json\",\n");
    fprintf(f, "  \"bomFormat\": \"CycloneDX\",\n");
    fprintf(f, "  \"specVersion\": \"1.5\",\n");
    fprintf(f, "  \"components\": [\n");

    for (size_t i = 0; i < eng->count; i++) {
        const audit_record_t *r = &eng->records[i];
        fprintf(f, "    {\n");
        fprintf(f, "      \"type\": \"library\",\n");
        fprintf(f, "      \"name\": \"%s\",\n", r->path);
        fprintf(f, "      \"version\": \"%s\",\n", r->index_sha);
        fprintf(f, "      \"purl\": \"pkg:generic/%s@%s\",\n", r->path, r->index_sha);
        fprintf(f, "      \"externalReferences\": [\n");
        fprintf(f, "        {\n");
        fprintf(f, "          \"type\": \"vcs\",\n");
        fprintf(f, "          \"url\": \"%s\"\n", r->url);
        fprintf(f, "        }\n");
        fprintf(f, "      ],\n");
        fprintf(f, "      \"licenses\": [\n");
        fprintf(f, "        {\n");
        fprintf(f, "          \"license\": {\n");
        fprintf(f, "            \"id\": \"%s\"\n", r->detected_license);
        fprintf(f, "          }\n");
        fprintf(f, "        }\n");
        fprintf(f, "      ],\n");
        fprintf(f, "      \"properties\": [\n");
        fprintf(f, "        {\"name\": \"audit:status\", \"value\": \"%d\"},\n", r->status);
        fprintf(f, "        {\"name\": \"audit:headSha\", \"value\": \"%s\"},\n", r->head_sha);
        fprintf(f, "        {\"name\": \"audit:depth\", \"value\": \"%d\"}\n", r->depth);
        fprintf(f, "      ]\n");
        fprintf(f, "    }%s\n", (i + 1 < eng->count) ? "," : "");
    }
    fprintf(f, "  ]\n}\n");
    fclose(f);
}

int main(int argc, char **argv) {
    const char *repo_root = (argc > 1) ? argv[1] : ".";

    audit_engine_t eng;
    if (!engine_init(&eng)) {
        fprintf(stderr, "Fatal error: memory allocation failure in audit engine\n");
        return 1;
    }

    audit_repository_recursive(repo_root, "", 0, &eng);
    print_audit_table(&eng);
    export_sbom_json("submodule-audit.json", &eng);

    bool has_critical_defects = false;
    for (size_t i = 0; i < eng.count; i++) {
        if (eng.records[i].status != STATUS_OK || eng.records[i].license_cat == LICENSE_STRONG_COPYLEFT) {
            has_critical_defects = true;
            break;
        }
    }

    engine_free(&eng);
    return has_critical_defects ? 1 : 0;
}
