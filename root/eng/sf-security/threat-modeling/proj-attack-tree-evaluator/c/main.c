#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    NODE_LEAF,
    NODE_OR,
    NODE_AND
} NodeType;

typedef struct {
    double damage;
    double reproducibility;
    double exploitability;
    double affected_users;
    double discoverability;
} DreadScore;

typedef struct AttackNode {
    char name[64];
    NodeType type;
    double cost;
    double probability;
    int skill_level;
    DreadScore dread;

    struct AttackNode** children;
    size_t children_count;
    size_t children_capacity;
} AttackNode;

AttackNode* create_leaf(const char* name, double cost, double probability, int skill, DreadScore dread) {
    AttackNode* node = (AttackNode*)malloc(sizeof(AttackNode));
    if (!node) return NULL;
    strncpy(node->name, name, sizeof(node->name) - 1);
    node->name[sizeof(node->name) - 1] = '\0';
    node->type = NODE_LEAF;
    node->cost = cost;
    node->probability = probability;
    node->skill_level = skill;
    node->dread = dread;
    node->children = NULL;
    node->children_count = 0;
    node->children_capacity = 0;
    return node;
}

AttackNode* create_operator(const char* name, NodeType type) {
    AttackNode* node = (AttackNode*)malloc(sizeof(AttackNode));
    if (!node) return NULL;
    strncpy(node->name, name, sizeof(node->name) - 1);
    node->name[sizeof(node->name) - 1] = '\0';
    node->type = type;
    node->cost = 0.0;
    node->probability = 0.0;
    node->skill_level = 0;
    memset(&node->dread, 0, sizeof(DreadScore));
    node->children = NULL;
    node->children_count = 0;
    node->children_capacity = 0;
    return node;
}

bool add_child(AttackNode* parent, AttackNode* child) {
    if (!parent || !child || parent->type == NODE_LEAF) return false;
    if (parent->children_count == parent->children_capacity) {
        size_t new_cap = parent->children_capacity == 0 ? 4 : parent->children_capacity * 2;
        AttackNode** new_buf = (AttackNode**)realloc(parent->children, new_cap * sizeof(AttackNode*));
        if (!new_buf) return false;
        parent->children = new_buf;
        parent->children_capacity = new_cap;
    }
    parent->children[parent->children_count++] = child;
    return true;
}

double calculate_dread_total(const DreadScore* d) {
    return (d->damage + d->reproducibility + d->exploitability + d->affected_users + d->discoverability) / 5.0;
}

void evaluate_tree(AttackNode* root) {
    if (!root || root->type == NODE_LEAF) return;

    for (size_t i = 0; i < root->children_count; ++i) {
        evaluate_tree(root->children[i]);
    }

    if (root->children_count == 0) return;

    if (root->type == NODE_OR) {
        double min_cost = root->children[0]->cost;
        double prod_inv_p = 1.0 - root->children[0]->probability;
        int min_skill = root->children[0]->skill_level;
        DreadScore max_dread = root->children[0]->dread;

        for (size_t i = 1; i < root->children_count; ++i) {
            AttackNode* c = root->children[i];
            if (c->cost < min_cost) min_cost = c->cost;
            prod_inv_p *= (1.0 - c->probability);
            if (c->skill_level < min_skill) min_skill = c->skill_level;
            if (calculate_dread_total(&c->dread) > calculate_dread_total(&max_dread)) {
                max_dread = c->dread;
            }
        }
        root->cost = min_cost;
        root->probability = 1.0 - prod_inv_p;
        root->skill_level = min_skill;
        root->dread = max_dread;
    } else if (root->type == NODE_AND) {
        double sum_cost = 0.0;
        double prod_p = 1.0;
        int max_skill = 0;
        DreadScore avg_dread = {0};

        for (size_t i = 0; i < root->children_count; ++i) {
            AttackNode* c = root->children[i];
            sum_cost += c->cost;
            prod_p *= c->probability;
            if (c->skill_level > max_skill) max_skill = c->skill_level;
            avg_dread.damage += c->dread.damage;
            avg_dread.reproducibility += c->dread.reproducibility;
            avg_dread.exploitability += c->dread.exploitability;
            avg_dread.affected_users += c->dread.affected_users;
            avg_dread.discoverability += c->dread.discoverability;
        }
        double n = (double)root->children_count;
        avg_dread.damage /= n;
        avg_dread.reproducibility /= n;
        avg_dread.exploitability /= n;
        avg_dread.affected_users /= n;
        avg_dread.discoverability /= n;

        root->cost = sum_cost;
        root->probability = prod_p;
        root->skill_level = max_skill;
        root->dread = avg_dread;
    }
}

void print_tree_report(const AttackNode* node, int indent) {
    if (!node) return;
    for (int i = 0; i < indent; ++i) printf("  ");
    const char* type_str = node->type == NODE_LEAF ? "LEAF" : (node->type == NODE_OR ? "OR" : "AND");
    printf("[%s] %s | Cost: %.0f грн | Prob: %.4f (%.2f%%) | Skill: %d | DREAD: %.1f/10\n",
           type_str, node->name, node->cost, node->probability, node->probability * 100.0,
           node->skill_level, calculate_dread_total(&node->dread));

    for (size_t i = 0; i < node->children_count; ++i) {
        print_tree_report(node->children[i], indent + 1);
    }
}

void free_tree(AttackNode* node) {
    if (!node) return;
    for (size_t i = 0; i < node->children_count; ++i) {
        free_tree(node->children[i]);
    }
    free(node->children);
    free(node);
}

int main(void) {
    AttackNode* root = create_operator("Злам платіжного шлюзу", NODE_OR);

    AttackNode* branch1 = create_operator("API підробка", NODE_AND);
    DreadScore d1 = {8.0, 7.0, 6.0, 9.0, 5.0};
    AttackNode* l1 = create_leaf("Фішинг API-ключа", 25000.0, 0.20, 2, d1);
    DreadScore d2 = {6.0, 8.0, 5.0, 4.0, 7.0};
    AttackNode* l2 = create_leaf("BGP/IP spoofing", 15000.0, 0.30, 3, d2);
    add_child(branch1, l1);
    add_child(branch1, l2);

    AttackNode* branch2 = create_operator("SQL-ін'єкція", NODE_AND);
    DreadScore d3 = {9.0, 9.0, 8.0, 10.0, 6.0};
    AttackNode* l3 = create_leaf("Виявлення SQLi", 10000.0, 0.10, 2, d3);
    DreadScore d4 = {7.0, 6.0, 5.0, 8.0, 4.0};
    AttackNode* l4 = create_leaf("Обхід WAF", 20000.0, 0.25, 3, d4);
    add_child(branch2, l3);
    add_child(branch2, l4);

    add_child(root, branch1);
    add_child(root, branch2);

    evaluate_tree(root);
    print_tree_report(root, 0);

    free_tree(root);
    return 0;
}
