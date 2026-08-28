/* kallsyms_resolver.c — Ідіоматична реалізація мовою C (POSIX C99) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>

#define MAX_LINE_LEN 256
#define MAX_SYM_NAME 128

typedef struct {
    uint64_t address;
    char type;
    char name[MAX_SYM_NAME];
    char module[64];
} symbol_entry_t;

typedef struct {
    symbol_entry_t *entries;
    size_t count;
    size_t capacity;
} symbol_table_t;

static int compare_by_address(const void *a, const void *b) {
    const symbol_entry_t *sa = (const symbol_entry_t *)a;
    const symbol_entry_t *sb = (const symbol_entry_t *)b;
    if (sa->address < sb->address) return -1;
    if (sa->address > sb->address) return 1;
    return 0;
}

symbol_table_t *symbol_table_load(const char *filepath) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        perror("Помилка відкриття /proc/kallsyms");
        return NULL;
    }

    symbol_table_t *table = malloc(sizeof(symbol_table_t));
    if (!table) {
        fclose(fp);
        return NULL;
    }

    table->capacity = 8192;
    table->count = 0;
    table->entries = malloc(table->capacity * sizeof(symbol_entry_t));
    if (!table->entries) {
        free(table);
        fclose(fp);
        return NULL;
    }

    char line[MAX_LINE_LEN];
    while (fgets(line, sizeof(line), fp)) {
        if (table->count >= table->capacity) {
            size_t new_cap = table->capacity * 2;
            symbol_entry_t *new_entries = realloc(table->entries, new_cap * sizeof(symbol_entry_t));
            if (!new_entries) break;
            table->entries = new_entries;
            table->capacity = new_cap;
        }

        symbol_entry_t *entry = &table->entries[table->count];
        entry->module[0] = '\0';

        int parsed = sscanf(line, "%lx %c %127s [%63[^]]]",
                            &entry->address, &entry->type,
                            entry->name, entry->module);

        if (parsed >= 3) {
            /* Перевірка маскування kptr_restrict */
            if (entry->address != 0) {
                table->count++;
            }
        }
    }

    fclose(fp);
    qsort(table->entries, table->count, sizeof(symbol_entry_t), compare_by_address);
    return table;
}

const symbol_entry_t *symbol_table_lookup(const symbol_table_t *table, uint64_t addr, uint64_t *out_offset) {
    if (!table || table->count == 0) return NULL;

    size_t low = 0;
    size_t high = table->count - 1;
    size_t best_idx = table->count;

    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        if (table->entries[mid].address <= addr) {
            best_idx = mid;
            low = mid + 1;
        } else {
            if (mid == 0) break;
            high = mid - 1;
        }
    }

    if (best_idx < table->count) {
        if (out_offset) {
            *out_offset = addr - table->entries[best_idx].address;
        }
        return &table->entries[best_idx];
    }
    return NULL;
}

void symbol_table_free(symbol_table_t *table) {
    if (table) {
        free(table->entries);
        free(table);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <hex_address>\n", argv[0]);
        return 1;
    }

    uint64_t target_addr = strtoull(argv[1], NULL, 16);
    symbol_table_t *table = symbol_table_load("/proc/kallsyms");
    if (!table) {
        fprintf(stderr, "Не вдалося завантажити таблицю символів. Перевірте kptr_restrict або права root.\n");
        return 1;
    }

    printf("Успішно завантажено %zu дійсних символів з /proc/kallsyms\n", table->count);

    uint64_t offset = 0;
    const symbol_entry_t *sym = symbol_table_lookup(table, target_addr, &offset);
    if (sym) {
        if (sym->module[0] != '\0') {
            printf("Адреса 0x%lx -> %s+0x%lx/??? [%s] (Тип: %c)\n",
                   target_addr, sym->name, offset, sym->module, sym->type);
        } else {
            printf("Адреса 0x%lx -> %s+0x%lx (Тип: %c)\n",
                   target_addr, sym->name, offset, sym->type);
        }
    } else {
        printf("Символ для адреси 0x%lx не знайдено.\n", target_addr);
    }

    symbol_table_free(table);
    return 0;
}
