#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LINE_LEN 1024
#define MAX_REFDES_LEN 32
#define MAX_STR_LEN 128
#define HASH_TABLE_CAPACITY 4096

typedef enum {
    LAYER_TOP = 0,
    LAYER_BOTTOM = 1,
    LAYER_UNKNOWN = 2
} pcb_layer_t;

typedef struct {
    char refdes[MAX_REFDES_LEN];
    char value[MAX_STR_LEN];
    char footprint[MAX_STR_LEN];
    char mpn[MAX_STR_LEN];
    bool is_dnp;
    bool matched_in_cpl;
} bom_entry_t;

typedef struct bom_node {
    bom_entry_t entry;
    struct bom_node *next;
} bom_node_t;

typedef struct {
    bom_node_t *buckets[HASH_TABLE_CAPACITY];
    size_t count;
} bom_table_t;

typedef struct {
    char refdes[MAX_REFDES_LEN];
    double mid_x;
    double mid_y;
    double rotation;
    pcb_layer_t layer;
    bool matched_in_bom;
} cpl_entry_t;

typedef struct {
    cpl_entry_t *items;
    size_t count;
    size_t capacity;
} cpl_list_t;

typedef struct {
    size_t missing_in_cpl;
    size_t extra_in_cpl;
    size_t dnp_with_cpl;
    size_t invalid_rotation;
    size_t total_errors;
} validation_stats_t;

/* Хеш-функція Dan Bernstein (djb2) для рядкових ключів */
static unsigned int hash_string(const char *str) {
    unsigned int hash = 5381;
    int c;
    while ((c = (unsigned char)*str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_TABLE_CAPACITY;
}

static char *trim_whitespace(char *str) {
    char *end;
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) return str;
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

static void strip_quotes(char *str) {
    size_t len = strlen(str);
    if (len >= 2 && str[0] == '"' && str[len - 1] == '"') {
        memmove(str, str + 1, len - 2);
        str[len - 2] = '\0';
    }
}

static void bom_table_init(bom_table_t *table) {
    memset(table->buckets, 0, sizeof(table->buckets));
    table->count = 0;
}

static bool bom_table_insert(bom_table_t *table, const bom_entry_t *entry) {
    unsigned int bucket = hash_string(entry->refdes);
    bom_node_t *curr = table->buckets[bucket];
    while (curr) {
        if (strcmp(curr->entry.refdes, entry->refdes) == 0) {
            return false; /* Дублювання RefDes у BOM */
        }
        curr = curr->next;
    }
    bom_node_t *new_node = (bom_node_t *)malloc(sizeof(bom_node_t));
    if (!new_node) return false;
    new_node->entry = *entry;
    new_node->next = table->buckets[bucket];
    table->buckets[bucket] = new_node;
    table->count++;
    return true;
}

static bom_entry_t *bom_table_lookup(bom_table_t *table, const char *refdes) {
    unsigned int bucket = hash_string(refdes);
    bom_node_t *curr = table->buckets[bucket];
    while (curr) {
        if (strcmp(curr->entry.refdes, refdes) == 0) {
            return &curr->entry;
        }
        curr = curr->next;
    }
    return NULL;
}

static void bom_table_free(bom_table_t *table) {
    for (size_t i = 0; i < HASH_TABLE_CAPACITY; i++) {
        bom_node_t *curr = table->buckets[i];
        while (curr) {
            bom_node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
        table->buckets[i] = NULL;
    }
    table->count = 0;
}

static void cpl_list_init(cpl_list_t *list) {
    list->items = NULL;
    list->count = 0;
    list->capacity = 0;
}

static bool cpl_list_append(cpl_list_t *list, const cpl_entry_t *entry) {
    if (list->count >= list->capacity) {
        size_t new_cap = list->capacity == 0 ? 64 : list->capacity * 2;
        cpl_entry_t *new_items = (cpl_entry_t *)realloc(list->items, new_cap * sizeof(cpl_entry_t));
        if (!new_items) return false;
        list->items = new_items;
        list->capacity = new_cap;
    }
    list->items[list->count++] = *entry;
    return true;
}

static void cpl_list_free(cpl_list_t *list) {
    free(list->items);
    list->items = NULL;
    list->count = 0;
    list->capacity = 0;
}

static pcb_layer_t parse_layer(const char *str) {
    if (strcasecmp(str, "Top") == 0 || strcasecmp(str, "T") == 0 || strcasecmp(str, "TopLayer") == 0) {
        return LAYER_TOP;
    }
    if (strcasecmp(str, "Bottom") == 0 || strcasecmp(str, "B") == 0 || strcasecmp(str, "BottomLayer") == 0) {
        return LAYER_BOTTOM;
    }
    return LAYER_UNKNOWN;
}

static const char *layer_to_string(pcb_layer_t layer) {
    switch (layer) {
        case LAYER_TOP: return "Top";
        case LAYER_BOTTOM: return "Bottom";
        default: return "Unknown";
    }
}

static void parse_and_insert_bom_refdes(bom_table_t *table, char *raw_refdes,
                                       const char *val, const char *footprint,
                                       const char *mpn, bool is_dnp) {
    strip_quotes(raw_refdes);
    char *token = strtok(raw_refdes, ",; ");
    while (token) {
        char *cleaned = trim_whitespace(token);
        if (strlen(cleaned) > 0) {
            bom_entry_t entry;
            memset(&entry, 0, sizeof(entry));
            strncpy(entry.refdes, cleaned, MAX_REFDES_LEN - 1);
            strncpy(entry.value, val, MAX_STR_LEN - 1);
            strncpy(entry.footprint, footprint, MAX_STR_LEN - 1);
            strncpy(entry.mpn, mpn, MAX_STR_LEN - 1);
            entry.is_dnp = is_dnp;
            entry.matched_in_cpl = false;
            bom_table_insert(table, &entry);
        }
        token = strtok(NULL, ",; ");
    }
}

static bool load_bom_csv(const char *filepath, bom_table_t *table) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        fprintf(stderr, "Помилка відкриття BOM файлу: %s\n", filepath);
        return false;
    }

    char line[MAX_LINE_LEN];
    bool is_header = true;

    while (fgets(line, sizeof(line), fp)) {
        char *trimmed = trim_whitespace(line);
        if (strlen(trimmed) == 0) continue;

        if (is_header) {
            is_header = false;
            continue;
        }

        char refdes_buf[MAX_STR_LEN] = {0};
        char val_buf[MAX_STR_LEN] = {0};
        char foot_buf[MAX_STR_LEN] = {0};
        char mpn_buf[MAX_STR_LEN] = {0};
        char dnp_buf[MAX_STR_LEN] = {0};

        int col = 0;
        char *ptr = trimmed;
        bool in_quotes = false;
        char *col_start = ptr;

        while (*ptr) {
            if (*ptr == '"') {
                in_quotes = !in_quotes;
            } else if (*ptr == ',' && !in_quotes) {
                *ptr = '\0';
                char *field = trim_whitespace(col_start);
                strip_quotes(field);
                if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
                else if (col == 1) strncpy(val_buf, field, sizeof(val_buf) - 1);
                else if (col == 2) strncpy(foot_buf, field, sizeof(foot_buf) - 1);
                else if (col == 3) strncpy(mpn_buf, field, sizeof(mpn_buf) - 1);
                else if (col == 4) strncpy(dnp_buf, field, sizeof(dnp_buf) - 1);
                col++;
                col_start = ptr + 1;
            }
            ptr++;
        }
        if (col_start <= ptr) {
            char *field = trim_whitespace(col_start);
            strip_quotes(field);
            if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
            else if (col == 1) strncpy(val_buf, field, sizeof(val_buf) - 1);
            else if (col == 2) strncpy(foot_buf, field, sizeof(foot_buf) - 1);
            else if (col == 3) strncpy(mpn_buf, field, sizeof(mpn_buf) - 1);
            else if (col == 4) strncpy(dnp_buf, field, sizeof(dnp_buf) - 1);
        }

        bool is_dnp = (strcmp(dnp_buf, "1") == 0 ||
                       strcasecmp(dnp_buf, "DNP") == 0 ||
                       strcasecmp(dnp_buf, "DNI") == 0 ||
                       strcasecmp(dnp_buf, "TRUE") == 0);

        parse_and_insert_bom_refdes(table, refdes_buf, val_buf, foot_buf, mpn_buf, is_dnp);
    }

    fclose(fp);
    return true;
}

static bool load_cpl_csv(const char *filepath, cpl_list_t *list) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        fprintf(stderr, "Помилка відкриття CPL файлу: %s\n", filepath);
        return false;
    }

    char line[MAX_LINE_LEN];
    bool is_header = true;

    while (fgets(line, sizeof(line), fp)) {
        char *trimmed = trim_whitespace(line);
        if (strlen(trimmed) == 0) continue;

        if (is_header) {
            is_header = false;
            continue;
        }

        char refdes_buf[MAX_REFDES_LEN] = {0};
        char x_buf[MAX_STR_LEN] = {0};
        char y_buf[MAX_STR_LEN] = {0};
        char layer_buf[MAX_STR_LEN] = {0};
        char rot_buf[MAX_STR_LEN] = {0};

        int col = 0;
        char *ptr = trimmed;
        bool in_quotes = false;
        char *col_start = ptr;

        while (*ptr) {
            if (*ptr == '"') {
                in_quotes = !in_quotes;
            } else if (*ptr == ',' && !in_quotes) {
                *ptr = '\0';
                char *field = trim_whitespace(col_start);
                strip_quotes(field);
                if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
                else if (col == 1) strncpy(x_buf, field, sizeof(x_buf) - 1);
                else if (col == 2) strncpy(y_buf, field, sizeof(y_buf) - 1);
                else if (col == 3) strncpy(layer_buf, field, sizeof(layer_buf) - 1);
                else if (col == 4) strncpy(rot_buf, field, sizeof(rot_buf) - 1);
                col++;
                col_start = ptr + 1;
            }
            ptr++;
        }
        if (col_start <= ptr) {
            char *field = trim_whitespace(col_start);
            strip_quotes(field);
            if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
            else if (col == 1) strncpy(x_buf, field, sizeof(x_buf) - 1);
            else if (col == 2) strncpy(y_buf, field, sizeof(y_buf) - 1);
            else if (col == 3) strncpy(layer_buf, field, sizeof(layer_buf) - 1);
            else if (col == 4) strncpy(rot_buf, field, sizeof(rot_buf) - 1);
        }

        if (strlen(refdes_buf) > 0) {
            cpl_entry_t entry;
            memset(&entry, 0, sizeof(entry));
            strncpy(entry.refdes, refdes_buf, sizeof(entry.refdes) - 1);
            entry.mid_x = atof(x_buf);
            entry.mid_y = atof(y_buf);
            entry.rotation = atof(rot_buf);
            entry.layer = parse_layer(layer_buf);
            entry.matched_in_bom = false;
            cpl_list_append(list, &entry);
        }
    }

    fclose(fp);
    return true;
}

static void validate_assembly_package(bom_table_t *bom, cpl_list_t *cpl, validation_stats_t *stats) {
    memset(stats, 0, sizeof(validation_stats_t));

    printf("=================================================================\n");
    printf("   ЗВІТ ВАЛІДАЦІЇ МОНТАЖНОГО ПАКЕТА (BOM <-> CPL MATCHING)\n");
    printf("=================================================================\n\n");

    for (size_t i = 0; i < cpl->count; i++) {
        cpl_entry_t *c_entry = &cpl->items[i];
        bom_entry_t *b_entry = bom_table_lookup(bom, c_entry->refdes);

        if (!b_entry) {
            printf("[ПОМИЛКА] CPL позиція '%s' відсутня в BOM (Фантомне розміщення)!\n", c_entry->refdes);
            printf("          Координати: (X=%.2f, Y=%.2f), Шар: %s, Кут: %.1f deg\n\n",
                   c_entry->mid_x, c_entry->mid_y, layer_to_string(c_entry->layer), c_entry->rotation);
            stats->extra_in_cpl++;
            stats->total_errors++;
        } else {
            c_entry->matched_in_bom = true;
            b_entry->matched_in_cpl = true;

            if (b_entry->is_dnp) {
                printf("[ПОПЕРЕДЖЕННЯ] Позиція '%s' позначена як DNP у BOM, але присутня в CPL!\n", c_entry->refdes);
                printf("               Деталь '%s' (%s) не повинна монтуватися на плату.\n\n",
                       b_entry->value, b_entry->mpn);
                stats->dnp_with_cpl++;
            }
        }

        if (c_entry->rotation < 0.0 || c_entry->rotation >= 360.0) {
            double normalized = fmod(fmod(c_entry->rotation, 360.0) + 360.0, 360.0);
            printf("[УВАГА] Позиція '%s' має ненормалізований кут: %.2f deg (Нормалізація -> %.2f deg)\n\n",
                   c_entry->refdes, c_entry->rotation, normalized);
            stats->invalid_rotation++;
        }
    }

    for (size_t i = 0; i < HASH_TABLE_CAPACITY; i++) {
        bom_node_t *node = bom->buckets[i];
        while (node) {
            if (!node->entry.matched_in_cpl && !node->entry.is_dnp) {
                printf("[ПОМИЛКА] BOM позиція '%s' відсутня в CPL файлі центроїдів!\n", node->entry.refdes);
                printf("          Номінал: %s, Корпус: %s, MPN: %s\n\n",
                       node->entry.value, node->entry.footprint, node->entry.mpn);
                stats->missing_in_cpl++;
                stats->total_errors++;
            }
            node = node->next;
        }
    }

    printf("-----------------------------------------------------------------\n");
    printf("ПІДСУМОК ПЕРЕВІРКИ:\n");
    printf("  - Усього записів у BOM : %zu\n", bom->count);
    printf("  - Усього записів у CPL : %zu\n", cpl->count);
    printf("  - Пропущено в CPL      : %zu\n", stats->missing_in_cpl);
    printf("  - Фантомних у CPL      : %zu\n", stats->extra_in_cpl);
    printf("  - DNP із координатами  : %zu\n", stats->dnp_with_cpl);
    printf("  - Ненормалізованих кутів: %zu\n", stats->invalid_rotation);
    printf("  - Критичних помилок    : %zu\n", stats->total_errors);
    printf("-----------------------------------------------------------------\n");

    if (stats->total_errors == 0) {
        printf("СТАТУС: МОНТАЖНИЙ ПАКЕТ ВАЛІДНИЙ (ГОТОВИЙ ДО ВИРОБНИЦТВА)\n");
    } else {
        printf("СТАТУС: ВИЯВЛЕНО НЕВІДПОВІДНОСТІ (ПОТРІБНЕ ВИПРАВЛЕННЯ САПР)\n");
    }
    printf("=================================================================\n");
}

int main(int argc, char **argv) {
    const char *bom_path = (argc > 1) ? argv[1] : "bom.csv";
    const char *cpl_path = (argc > 2) ? argv[2] : "cpl.csv";

    bom_table_t bom;
    cpl_list_t cpl;
    validation_stats_t stats;

    bom_table_init(&bom);
    cpl_list_init(&cpl);

    printf("Завантаження BOM: %s ...\n", bom_path);
    if (!load_bom_csv(bom_path, &bom)) {
        bom_table_free(&bom);
        cpl_list_free(&cpl);
        return 1;
    }

    printf("Завантаження CPL: %s ...\n", cpl_path);
    if (!load_cpl_csv(cpl_path, &cpl)) {
        bom_table_free(&bom);
        cpl_list_free(&cpl);
        return 1;
    }

    validate_assembly_package(&bom, &cpl, &stats);

    bom_table_free(&bom);
    cpl_list_free(&cpl);

    return (stats.total_errors == 0) ? 0 : 2;
}
