#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_NETS 128
#define MAX_PINS_PER_NET 64
#define MAX_NAME_LEN 32

typedef struct {
    char refdes[16];
    char pin[8];
    double x_mm;
    double y_mm;
    int is_smd;
} testpoint_t;

typedef struct {
    char net_name[MAX_NAME_LEN];
    testpoint_t points[MAX_PINS_PER_NET];
    size_t point_count;
} net_entry_t;

typedef struct {
    net_entry_t nets[MAX_NETS];
    size_t net_count;
} netlist_db_t;

static void trim_spaces(char *str) {
    char *end;
    while (isspace((unsigned char)*str)) str++;
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
}

static net_entry_t *find_or_add_net(netlist_db_t *db, const char *net_name) {
    for (size_t i = 0; i < db->net_count; ++i) {
        if (strcmp(db->nets[i].net_name, net_name) == 0) {
            return &db->nets[i];
        }
    }
    if (db->net_count >= MAX_NETS) return NULL;
    net_entry_t *entry = &db->nets[db->net_count++];
    strncpy(entry->net_name, net_name, MAX_NAME_LEN - 1);
    entry->net_name[MAX_NAME_LEN - 1] = '\0';
    entry->point_count = 0;
    return entry;
}

int parse_ipc_line(netlist_db_t *db, const char *line) {
    if (!line || line[0] == 'C' || line[0] == 'P' || line[0] == '\0' || isspace((unsigned char)line[0])) {
        return 0; // Пропуск коментарів, директив параметрів та порожніх рядків
    }

    int opcode = 0;
    char net_name[MAX_NAME_LEN] = {0};
    char refdes[16] = {0};
    char pin_raw[16] = {0};
    
    // Парсинг перших токенів: Опкод, Ім'я кола, RefDes, Pin
    if (sscanf(line, "%d %31s %15s %15s", &opcode, net_name, refdes, pin_raw) < 4) {
        return -1;
    }

    // Видалення дефісу з номера піна (наприклад, "-14" -> "14")
    const char *pin = (pin_raw[0] == '-') ? pin_raw + 1 : pin_raw;

    // Пошук координат X та Y у рядку (шаблон X+010500 Y+020000)
    double x_val = 0.0, y_val = 0.0;
    const char *x_ptr = strstr(line, "X+");
    if (!x_ptr) x_ptr = strstr(line, "X-");
    const char *y_ptr = strstr(line, "Y+");
    if (!y_ptr) y_ptr = strstr(line, "Y-");

    if (x_ptr) x_val = atof(x_ptr + 1) / 1000.0; // переведення у мм
    if (y_ptr) y_val = atof(y_ptr + 1) / 1000.0;

    net_entry_t *net = find_or_add_net(db, net_name);
    if (!net || net->point_count >= MAX_PINS_PER_NET) {
        return -1;
    }

    testpoint_t *pt = &net->points[net->point_count++];
    strncpy(pt->refdes, refdes, sizeof(pt->refdes) - 1);
    strncpy(pt->pin, pin, sizeof(pt->pin) - 1);
    pt->x_mm = x_val;
    pt->y_mm = y_val;
    pt->is_smd = (opcode == 327);

    return 1;
}

void print_netlist_summary(const netlist_db_t *db) {
    printf("=== Звіт розбору списку з'єднань (IPC-D-356) ===\n");
    printf("Знайдено унікальних мереж: %zu\n\n", db->net_count);
    for (size_t i = 0; i < db->net_count; ++i) {
        const net_entry_t *net = &db->nets[i];
        printf("Мережа [%s] — точок з'єднання: %zu\n", net->net_name, net->point_count);
        for (size_t p = 0; p < net->point_count; ++p) {
            const testpoint_t *pt = &net->points[p];
            printf("  -> Вузол %s.%s (%s) на (%.2f, %.2f) мм\n",
                   pt->refdes, pt->pin,
                   pt->is_smd ? "SMD" : "THT",
                   pt->x_mm, pt->y_mm);
        }
    }
}

int main(void) {
    const char *sample_ipc_data =
        "C  IPC-D-356 Test Netlist\n"
        "P  UNITS CUST\n"
        "317 VCC_3V3       U1   -14   M D0030A0050P0000X+010500Y+020000X0030Y0050\n"
        "327 VCC_3V3       C1   -1    M D0020A0040P0000X+012000Y+019500X0020Y0040\n"
        "327 VCC_3V3       R1   -2    M D0020A0040P0000X+015200Y+022100X0020Y0040\n"
        "317 GND           U1   -7    M D0030A0050P0000X+010500Y+027000X0030Y0050\n"
        "327 GND           C1   -2    M D0020A0040P0000X+012000Y+026500X0020Y0040\n"
        "317 SPI_MOSI      U1   -5    M D0030A0050P0000X+010500Y+023000X0030Y0050\n"
        "327 SPI_MOSI      R2   -1    M D0020A0040P0000X+018000Y+023000X0020Y0040\n";

    netlist_db_t db = {0};
    char buffer[256];
    const char *cursor = sample_ipc_data;

    while (*cursor) {
        size_t len = 0;
        while (cursor[len] && cursor[len] != '\n' && len < sizeof(buffer) - 1) {
            len++;
        }
        strncpy(buffer, cursor, len);
        buffer[len] = '\0';
        cursor += len + (cursor[len] == '\n' ? 1 : 0);

        parse_ipc_line(&db, buffer);
    }

    print_netlist_summary(&db);
    return 0;
}
