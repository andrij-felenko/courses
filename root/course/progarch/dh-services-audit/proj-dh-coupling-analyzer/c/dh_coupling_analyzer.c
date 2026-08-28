/* dh_coupling_analyzer.c — Парсер зчеплення SQL-запитів та розрахунок Extraction Score мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_TABLES 16
#define MAX_CONTEXTS 8
#define MAX_STR 128

typedef struct {
    char name[MAX_STR];
    char tables[MAX_TABLES][MAX_STR];
    int table_count;
    double resource_asymmetry;
    double deploy_autonomy;
    double fault_isolation;
    double compliance_wall;
} BoundedContext;

typedef struct {
    char context_a[MAX_STR];
    char context_b[MAX_STR];
    int cross_join_count;
} CouplingEdge;

typedef struct {
    BoundedContext contexts[MAX_CONTEXTS];
    int context_count;
    CouplingEdge edges[MAX_CONTEXTS * MAX_CONTEXTS];
    int edge_count;
} AuditSystem;

static void init_audit_system(AuditSystem *sys) {
    sys->context_count = 0;
    sys->edge_count = 0;
}

static void add_context(AuditSystem *sys, const char *name, double res, double dep, double fault, double comp) {
    if (sys->context_count >= MAX_CONTEXTS) return;
    BoundedContext *ctx = &sys->contexts[sys->context_count++];
    strncpy(ctx->name, name, MAX_STR - 1);
    ctx->table_count = 0;
    ctx->resource_asymmetry = res;
    ctx->deploy_autonomy = dep;
    ctx->fault_isolation = fault;
    ctx->compliance_wall = comp;
}

static void add_table_to_context(AuditSystem *sys, const char *context_name, const char *table_name) {
    for (int i = 0; i < sys->context_count; i++) {
        if (strcmp(sys->contexts[i].name, context_name) == 0) {
            BoundedContext *ctx = &sys->contexts[i];
            if (ctx->table_count < MAX_TABLES) {
                strncpy(ctx->tables[ctx->table_count++], table_name, MAX_STR - 1);
            }
            return;
        }
    }
}

static const char* find_context_by_table(const AuditSystem *sys, const char *table_name) {
    for (int i = 0; i < sys->context_count; i++) {
        for (int j = 0; j < sys->contexts[i].table_count; j++) {
            if (strcmp(sys->contexts[i].tables[j], table_name) == 0) {
                return sys->contexts[i].name;
            }
        }
    }
    return NULL;
}

static void record_sql_query(AuditSystem *sys, const char *sql_query) {
    char table1[MAX_STR] = {0};
    char table2[MAX_STR] = {0};

    /* Простий аналіз наявності таблиць у SQL JOIN запиті */
    if (strstr(sql_query, "JOIN") != NULL || strstr(sql_query, "join") != NULL) {
        if (sscanf(sql_query, "SELECT %*s FROM %127s JOIN %127s", table1, table2) >= 2 ||
            sscanf(sql_query, "select %*s from %127s join %127s", table1, table2) >= 2) {
            
            const char *ctx_a = find_context_by_table(sys, table1);
            const char *ctx_b = find_context_by_table(sys, table2);

            if (ctx_a != NULL && ctx_b != NULL && strcmp(ctx_a, ctx_b) != 0) {
                /* Знайдено міждоменний JOIN — фіксуємо зчеплення */
                bool found = false;
                for (int i = 0; i < sys->edge_count; i++) {
                    if ((strcmp(sys->edges[i].context_a, ctx_a) == 0 && strcmp(sys->edges[i].context_b, ctx_b) == 0) ||
                        (strcmp(sys->edges[i].context_a, ctx_b) == 0 && strcmp(sys->edges[i].context_b, ctx_a) == 0)) {
                        sys->edges[i].cross_join_count++;
                        found = true;
                        break;
                    }
                }
                if (!found && sys->edge_count < MAX_CONTEXTS * MAX_CONTEXTS) {
                    CouplingEdge *edge = &sys->edges[sys->edge_count++];
                    strncpy(edge->context_a, ctx_a, MAX_STR - 1);
                    strncpy(edge->context_b, ctx_b, MAX_STR - 1);
                    edge->cross_join_count = 1;
                }
            }
        }
    }
}

static double calculate_extraction_score(const AuditSystem *sys, const BoundedContext *ctx) {
    int total_cross_joins = 0;
    for (int i = 0; i < sys->edge_count; i++) {
        if (strcmp(sys->edges[i].context_a, ctx->name) == 0 ||
            strcmp(sys->edges[i].context_b, ctx->name) == 0) {
            total_cross_joins += sys->edges[i].cross_join_count;
        }
    }

    double data_coupling_penalty = total_cross_joins * 1.5;
    
    double score = (2.5 * ctx->resource_asymmetry) +
                   (2.0 * ctx->deploy_autonomy) +
                   (3.0 * ctx->fault_isolation) +
                   (3.5 * ctx->compliance_wall) -
                   data_coupling_penalty;

    return score;
}

int main(void) {
    AuditSystem sys;
    init_audit_system(&sys);

    /* Ініціалізація доменів Digital Homes */
    add_context(&sys, "dh-telemetry", 9.5, 8.0, 4.0, 0.0);
    add_table_to_context(&sys, "dh-telemetry", "telemetry_events");

    add_context(&sys, "dh-video", 9.0, 6.0, 9.5, 0.0);
    add_table_to_context(&sys, "dh-video", "video_feeds");

    add_context(&sys, "dh-device-mgmt", 3.0, 3.0, 2.0, 0.0);
    add_table_to_context(&sys, "dh-device-mgmt", "devices");

    add_context(&sys, "dh-digital-twin", 4.0, 4.0, 2.0, 0.0);
    add_table_to_context(&sys, "dh-digital-twin", "device_states");

    /* Імітація обробки SQL логів */
    record_sql_query(&sys, "SELECT * FROM device_states JOIN devices ON device_states.id = devices.id");
    record_sql_query(&sys, "SELECT * FROM device_states JOIN devices ON device_states.id = devices.id");
    record_sql_query(&sys, "SELECT * FROM telemetry_events WHERE id = 1");

    printf("=== Результати сервіс-аудиту Digital Homes (C version) ===\n");
    for (int i = 0; i < sys.context_count; i++) {
        const BoundedContext *ctx = &sys.contexts[i];
        double score = calculate_extraction_score(&sys, ctx);
        printf("Домен: %-18s | Extraction Score: %6.1f | Вердикт: %s\n",
               ctx->name, score,
               (score >= 15.0) ? "🟢 ВИДІЛЯТИ СЕРВІС" : "🔴 ЗАЛИШИТИ В МОНОЛІТІ");
    }

    return 0;
}
