#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_MODULES 16
#define MAX_NAME_LEN 32

typedef struct {
    char name[MAX_NAME_LEN];
    int layer_level; /* 0 = Domain, 1 = Service, 2 = Infrastructure/Web */
} Module;

typedef struct {
    int module_count;
    Module modules[MAX_MODULES];
    bool adj[MAX_MODULES][MAX_MODULES]; /* adj[i][j] = true означає i залежить від j */
} DependencyGraph;

void graph_init(DependencyGraph *g) {
    g->module_count = 0;
    memset(g->adj, 0, sizeof(g->adj));
}

int graph_add_module(DependencyGraph *g, const char *name, int layer) {
    if (g->module_count >= MAX_MODULES) return -1;
    int id = g->module_count++;
    strncpy(g->modules[id].name, name, MAX_NAME_LEN - 1);
    g->modules[id].name[MAX_NAME_LEN - 1] = '\0';
    g->modules[id].layer_level = layer;
    return id;
}

void graph_add_dependency(DependencyGraph *g, int from_id, int to_id) {
    if (from_id >= 0 && from_id < g->module_count &&
        to_id >= 0 && to_id < g->module_count) {
        g->adj[from_id][to_id] = true;
    }
}

void analyze_instability(const DependencyGraph *g) {
    printf("=== АНАЛІЗ НЕСТАБІЛЬНОСТІ МОДУЛІВ (I = Ce / (Ca + Ce)) ===\n");
    for (int i = 0; i < g->module_count; i++) {
        int ca = 0; /* вхідні залежності (хто залежить від i) */
        int ce = 0; /* вихідні залежності (від кого залежить i) */

        for (int j = 0; j < g->module_count; j++) {
            if (i == j) continue;
            if (g->adj[i][j]) ce++;
            if (g->adj[j][i]) ca++;
        }

        double instability = 0.0;
        if (ca + ce > 0) {
            instability = (double)ce / (ca + ce);
        }

        printf("Модуль [%-15s] (Шар %d): Ca=%2d, Ce=%2d => Нестабільність I = %.2f\n",
               g->modules[i].name, g->modules[i].layer_level, ca, ce, instability);
    }
}

bool check_layer_violations(const DependencyGraph *g) {
    printf("\n=== ПЕРЕВІРКА ПРАВИЛ ШАРІВ ТА ПОРОШЕНЬ АРХІТЕКТУРИ ===\n");
    bool violations_found = false;

    for (int i = 0; i < g->module_count; i++) {
        for (int j = 0; j < g->module_count; j++) {
            if (i == j) continue;

            if (g->adj[i][j]) {
                /* Якщо модуль з нижчого шару посилається на вищий шар */
                if (g->modules[i].layer_level < g->modules[j].layer_level) {
                    printf("❌ КРИТИЧНИЙ ДЕФЕКТ: Модуль шару %d [%s] залежить від модуля вищого шару %d [%s]!\n",
                           g->modules[i].layer_level, g->modules[i].name,
                           g->modules[j].layer_level, g->modules[j].name);
                    violations_found = true;
                }
            }
        }
    }

    if (!violations_found) {
        printf("✅ ПОРОШЕНЬ ШАРІВ НЕ ВИЯВЛЕНО: Архітектурні межі дотримано!\n");
    }
    return !violations_found;
}

int main(void) {
    DependencyGraph g;
    graph_init(&g);

    int m_domain = graph_add_module(&g, "DomainCore", 0);
    int m_usecase = graph_add_module(&g, "OrderUseCase", 1);
    int m_db_adapter = graph_add_module(&g, "PostgresAdapter", 2);
    int m_web_ctrl = graph_add_module(&g, "HttpController", 2);

    /* Дозволені залежності */
    graph_add_dependency(&g, m_web_ctrl, m_usecase);    /* Controller -> UseCase */
    graph_add_dependency(&g, m_db_adapter, m_domain);   /* Adapter -> Domain */
    graph_add_dependency(&g, m_usecase, m_domain);      /* UseCase -> Domain */

    /* ІМІТАЦІЯ ДЕФЕКТУ: Доменна сутність випадково викликає DB Adapter */
    /* graph_add_dependency(&g, m_domain, m_db_adapter); */

    analyze_instability(&g);
    bool pass = check_layer_violations(&g);

    return pass ? 0 : 1;
}
