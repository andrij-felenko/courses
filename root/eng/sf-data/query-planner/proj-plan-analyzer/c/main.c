#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

typedef struct PlanNode {
    char node_type[64];
    char relation_name[64];
    double startup_cost;
    double total_cost;
    double plan_rows;
    double actual_time_ms;
    double actual_rows;
    int actual_loops;
    long shared_hit_blocks;
    long shared_read_blocks;
    long rows_removed_filter;
    bool spilled_to_disk;
    
    struct PlanNode** children;
    size_t children_count;
    size_t children_capacity;
} PlanNode;

typedef struct {
    int total_nodes;
    int cardinality_warnings;
    int disk_spills;
    int filter_warnings;
    long total_shared_hit;
    long total_shared_read;
} DiagnosticSummary;

PlanNode* create_plan_node(const char* type, const char* rel, double cost, 
                          double plan_r, double act_time, double act_r, int loops) {
    PlanNode* node = (PlanNode*)calloc(1, sizeof(PlanNode));
    if (!node) return NULL;
    
    strncpy(node->node_type, type, sizeof(node->node_type) - 1);
    if (rel) strncpy(node->relation_name, rel, sizeof(node->relation_name) - 1);
    
    node->total_cost = cost;
    node->plan_rows = plan_r;
    node->actual_time_ms = act_time;
    node->actual_rows = act_r;
    node->actual_loops = loops;
    return node;
}

void add_child_node(PlanNode* parent, PlanNode* child) {
    if (!parent || !child) return;
    if (parent->children_count >= parent->children_capacity) {
        size_t new_cap = parent->children_capacity == 0 ? 2 : parent->children_capacity * 2;
        PlanNode** new_children = (PlanNode**)realloc(parent->children, new_cap * sizeof(PlanNode*));
        if (!new_children) return;
        parent->children = new_children;
        parent->children_capacity = new_cap;
    }
    parent->children[parent->children_count++] = child;
}

void analyze_node_recursive(const PlanNode* node, int depth, DiagnosticSummary* summary) {
    if (!node) return;
    summary->total_nodes++;
    summary->total_shared_hit += node->shared_hit_blocks;
    summary->total_shared_read += node->shared_read_blocks;

    double total_actual_rows = node->actual_rows * node->actual_loops;
    double ratio = node->plan_rows > 0 ? total_actual_rows / node->plan_rows : 1.0;

    // Відступ для візуалізації ієрархії дерева
    for (int i = 0; i < depth; ++i) printf("  ");
    printf("-> %s", node->node_type);
    if (strlen(node->relation_name) > 0) printf(" on %s", node->relation_name);
    printf(" (cost=%.2f, act_time=%.2f ms, act_rows=%.0f, plan_rows=%.0f)\n",
           node->total_cost, node->actual_time_ms * node->actual_loops,
           total_actual_rows, node->plan_rows);

    // 1. Перевірка помилки кардинальності
    if ((ratio > 10.0 || ratio < 0.1) && total_actual_rows > 100.0) {
        summary->cardinality_warnings++;
        for (int i = 0; i < depth + 1; ++i) printf("  ");
        printf("⚠️  [УВАГА: Кардинальність] Прогноз %.0f рядків, факт: %.0f (коефіцієнт %.1fx)\n",
               node->plan_rows, total_actual_rows, ratio);
    }

    // 2. Перевірка скидання на диск
    if (node->spilled_to_disk) {
        summary->disk_spills++;
        for (int i = 0; i < depth + 1; ++i) printf("  ");
        printf("⚠️  [КРИТИЧНО: Диск] Вузол скинув дані на диск через нестачу work_mem!\n");
    }

    // 3. Перевірка надмірної фільтрації
    if (node->rows_removed_filter > 10000) {
        summary->filter_warnings++;
        for (int i = 0; i < depth + 1; ++i) printf("  ");
        printf("⚠️  [УВАГА: Фільтр] Відкинуто %ld рядків предиката. Потрібен індекс!\n",
               node->rows_removed_filter);
    }

    for (size_t i = 0; i < node->children_count; ++i) {
        analyze_node_recursive(node->children[i], depth + 1, summary);
    }
}

void print_diagnostic_report(const PlanNode* root) {
    printf("================ ЗВІТ АНАЛІЗУ ПЛАНУ EXPLAIN ================\n");
    DiagnosticSummary summary = {0};
    analyze_node_recursive(root, 0, &summary);

    printf("\n----------------------- ПІДСУМОК -----------------------\n");
    printf("Всього вузлів у дереві: %d\n", summary.total_nodes);
    printf("Помилок кардинальності: %d\n", summary.cardinality_warnings);
    printf("Скидань на диск:       %d\n", summary.disk_spills);
    printf("Вузлів із високою фільтрацією: %d\n", summary.filter_warnings);

    long total_blocks = summary.total_shared_hit + summary.total_shared_read;
    if (total_blocks > 0) {
        double hit_ratio = (double)summary.total_shared_hit / (double)total_blocks * 100.0;
        printf("Ефективність кешу (Hit Ratio): %.2f%% (%ld hit, %ld read)\n",
               hit_ratio, summary.total_shared_hit, summary.total_shared_read);
        if (hit_ratio < 95.0 && summary.total_shared_read > 500) {
            printf("⚠️  [УВАГА: Кеш] Hit ratio нижчий за 95%%. Можливий дефіцит пам'яті.\n");
        }
    }
    printf("============================================================\n");
}

void free_plan_tree(PlanNode* node) {
    if (!node) return;
    for (size_t i = 0; i < node->children_count; ++i) {
        free_plan_tree(node->children[i]);
    }
    free(node->children);
    free(node);
}

int main(void) {
    // Демонстраційна побудова плану для SELECT * FROM orders JOIN users ON ...
    PlanNode* root = create_plan_node("Hash Join", NULL, 942.50, 4300, 14.30, 4120, 1);
    root->shared_hit_blocks = 1200;
    root->shared_read_blocks = 450;

    PlanNode* scan_orders = create_plan_node("Seq Scan", "orders", 540.00, 15000, 6.80, 15000, 1);
    scan_orders->rows_removed_filter = 35000;
    scan_orders->shared_hit_blocks = 800;
    scan_orders->shared_read_blocks = 400;

    PlanNode* hash_node = create_plan_node("Hash", NULL, 160.00, 1200, 0.74, 1180, 1);
    PlanNode* scan_users = create_plan_node("Index Scan", "users", 160.00, 120, 0.52, 1180, 1);
    scan_users->shared_hit_blocks = 400;
    scan_users->shared_read_blocks = 50;

    add_child_node(hash_node, scan_users);
    add_child_node(root, scan_orders);
    add_child_node(root, hash_node);

    print_diagnostic_report(root);
    free_plan_tree(root);
    return 0;
}
