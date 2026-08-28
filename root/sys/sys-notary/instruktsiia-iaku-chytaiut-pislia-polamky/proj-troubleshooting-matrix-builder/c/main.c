#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_NODES 32
#define MAX_TEXT_LEN 128

typedef enum {
    NODE_SYMPTOM,
    NODE_CHECK,
    NODE_ACTION
} NodeType;

typedef struct {
    uint32_t id;
    NodeType type;
    char description[MAX_TEXT_LEN];
    int32_t next_pass_id;  /* ID вузла при успішній перевірці (або єдиний перехід) */
    int32_t next_fail_id;  /* ID вузла при невдалій перевірці (тільки для NODE_CHECK) */
} DiagNode;

typedef struct {
    DiagNode nodes[MAX_NODES];
    size_t count;
} DiagGraph;

void graph_init(DiagGraph *graph) {
    if (!graph) return;
    graph->count = 0;
}

bool graph_add_node(DiagGraph *graph, uint32_t id, NodeType type, const char *desc,
                    int32_t pass_id, int32_t fail_id) {
    if (!graph || graph->count >= MAX_NODES) return false;
    
    DiagNode *node = &graph->nodes[graph->count++];
    node->id = id;
    node->type = type;
    strncpy(node->description, desc, MAX_TEXT_LEN - 1);
    node->description[MAX_TEXT_LEN - 1] = '\0';
    node->next_pass_id = pass_id;
    node->next_fail_id = fail_id;
    return true;
}

static const DiagNode* graph_find_node(const DiagGraph *graph, int32_t id) {
    if (!graph || id < 0) return NULL;
    for (size_t i = 0; i < graph->count; ++i) {
        if ((int32_t)graph->nodes[i].id == id) {
            return &graph->nodes[i];
        }
    }
    return NULL;
}

static bool check_path_to_action(const DiagGraph *graph, const DiagNode *curr,
                                 bool visited[MAX_NODES]) {
    if (!curr) return false;
    if (curr->type == NODE_ACTION) return true;

    /* Пошук індексу поточного вузла у масиві для захисту від зациклення */
    size_t idx = 0;
    for (; idx < graph->count; ++idx) {
        if (graph->nodes[idx].id == curr->id) break;
    }
    if (idx >= graph->count || visited[idx]) {
        return false; /* Виявлено нескінченний цикл без виходу на дію */
    }
    visited[idx] = true;

    bool pass_ok = false;
    bool fail_ok = false;

    if (curr->type == NODE_SYMPTOM) {
        const DiagNode *next = graph_find_node(graph, curr->next_pass_id);
        pass_ok = check_path_to_action(graph, next, visited);
        visited[idx] = false;
        return pass_ok;
    }

    if (curr->type == NODE_CHECK) {
        const DiagNode *pass_node = graph_find_node(graph, curr->next_pass_id);
        const DiagNode *fail_node = graph_find_node(graph, curr->next_fail_id);

        if (!pass_node || !fail_node) {
            visited[idx] = false;
            return false; /* Глухий кут: відсутній один із переходів */
        }

        bool visited_pass[MAX_NODES];
        bool visited_fail[MAX_NODES];
        memcpy(visited_pass, visited, sizeof(bool) * MAX_NODES);
        memcpy(visited_fail, visited, sizeof(bool) * MAX_NODES);

        pass_ok = check_path_to_action(graph, pass_node, visited_pass);
        fail_ok = check_path_to_action(graph, fail_node, visited_fail);
        visited[idx] = false;
        return pass_ok && fail_ok;
    }

    visited[idx] = false;
    return false;
}

bool graph_validate(const DiagGraph *graph, char *err_buf, size_t buf_size) {
    if (!graph || graph->count == 0) {
        snprintf(err_buf, buf_size, "Помилка: граф порожній");
        return false;
    }

    for (size_t i = 0; i < graph->count; ++i) {
        const DiagNode *n = &graph->nodes[i];
        if (n->type == NODE_SYMPTOM) {
            bool visited[MAX_NODES] = {false};
            if (!check_path_to_action(graph, n, visited)) {
                snprintf(err_buf, buf_size, "Помилка: від симптому [ID %u: %s] "
                         "немає повного шляху до дії", n->id, n->description);
                return false;
            }
        }
    }

    snprintf(err_buf, buf_size, "Граф валідний: усі гілки завершуються діями, циклів немає");
    return true;
}

void graph_simulate_troubleshooting(const DiagGraph *graph, uint32_t start_symptom_id) {
    const DiagNode *curr = graph_find_node(graph, (int32_t)start_symptom_id);
    if (!curr || curr->type != NODE_SYMPTOM) {
        printf("[СИСТЕМА] Симптом ID %u не знайдено.\n", start_symptom_id);
        return;
    }

    printf("\n=== ПОЧАТОК СЕАНСУ ДІАГНОСТИКИ ===\n");
    printf("[СИМПТОМ] ID %u: %s\n", curr->id, curr->description);
    curr = graph_find_node(graph, curr->next_pass_id);

    while (curr) {
        if (curr->type == NODE_CHECK) {
            printf("\n[ПЕРЕВІРКА ID %u]: %s\n", curr->id, curr->description);
            printf("Результат тесту (1 - ТАК/PASS, 0 - НІ/FAIL): 0\n");
            /* Симуляція негативного результату для демонстрації гілки */
            int choice = 0;
            if (choice == 1) {
                curr = graph_find_node(graph, curr->next_pass_id);
            } else {
                curr = graph_find_node(graph, curr->next_fail_id);
            }
        } else if (curr->type == NODE_ACTION) {
            printf("\n[ВІДНОВЛЮВАЛЬНА ДІЯ ID %u]:\n-> %s\n", curr->id, curr->description);
            printf("=== ДІАГНОСТИКУ ЗАВЕРШЕНО ===\n");
            break;
        } else {
            break;
        }
    }
}

int main(void) {
    DiagGraph g;
    graph_init(&g);

    /* Побудова тестового діагностичного дерева */
    graph_add_node(&g, 1, NODE_SYMPTOM, "Червоний світлодіод STATUS блимає кожні 2 с", 2, -1);
    graph_add_node(&g, 2, NODE_CHECK, "Напруга живлення V+ у межах 18..30 В DC?", 3, 101);
    graph_add_node(&g, 101, NODE_ACTION, "Замінити запобіжник 24 В та перевірити блок живлення", -1, -1);
    graph_add_node(&g, 3, NODE_CHECK, "Термінація RS-485 на шині дорівнює 60 Ом?", 4, 102);
    graph_add_node(&g, 102, NODE_ACTION, "Увімкнути термінатор 120 Ом на кінцевих вузлах", -1, -1);
    graph_add_node(&g, 4, NODE_ACTION, "Перевірити унікальність Modbus ID та швидкість зв'язку", -1, -1);

    char report[256];
    bool ok = graph_validate(&g, report, sizeof(report));
    printf("Результат валідації: %s\n", report);

    if (ok) {
        graph_simulate_troubleshooting(&g, 1);
    }
    return 0;
}
