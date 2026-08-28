#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define BT_MAX_CHILDREN      8
#define BT_MAX_NODES         32
#define BT_MAX_BB_ENTRIES    16
#define BT_KEY_LEN           24

/* Статуси виконання вузла */
typedef enum {
    BT_STATUS_IDLE = 0,
    BT_STATUS_RUNNING,
    BT_STATUS_SUCCESS,
    BT_STATUS_FAILURE
} bt_status_t;

/* Типи вузлів дерева поведінки */
typedef enum {
    BT_NODE_ACTION,
    BT_NODE_CONDITION,
    BT_NODE_SEQUENCE,
    BT_NODE_REACTIVE_SEQUENCE,
    BT_NODE_FALLBACK,
    BT_NODE_REACTIVE_FALLBACK,
    BT_NODE_PARALLEL_M_OF_N,
    BT_NODE_INVERTER,
    BT_NODE_TIMEOUT
} bt_node_type_t;

/* Типи даних Дошки Оголошень */
typedef enum {
    BB_TYPE_EMPTY = 0,
    BB_TYPE_BOOL,
    BB_TYPE_INT32,
    BB_TYPE_FLOAT
} bb_val_type_t;

typedef struct {
    char key[BT_KEY_LEN];
    bb_val_type_t type;
    union {
        bool b_val;
        int32_t i_val;
        float f_val;
    } data;
    bool is_set;
} bb_entry_t;

typedef struct {
    bb_entry_t entries[BT_MAX_BB_ENTRIES];
    uint8_t count;
} blackboard_t;

/* Попереднє оголошення вузла */
struct bt_node;
typedef bt_status_t (*bt_tick_fn)(struct bt_node *self, blackboard_t *bb);
typedef void (*bt_halt_fn)(struct bt_node *self, blackboard_t *bb);

/* Дескриптор вузла дерева */
typedef struct bt_node {
    uint8_t id;
    bt_node_type_t type;
    bt_status_t status;
    bt_tick_fn tick_fn;
    bt_halt_fn halt_fn;
    uint8_t children[BT_MAX_CHILDREN];
    uint8_t child_count;
    uint8_t running_child_idx;
    uint8_t threshold_m;          /* Для паралельного вузла: поріг успішних дітей */
    uint32_t timeout_ticks;       /* Для декоратора Timeout: ліміт тактів */
    uint32_t elapsed_ticks;       /* Поточний лічильник тактів */
    void *user_data;              /* Вказівник на локальний контекст */
} bt_node_t;

/* Статичний контекст дерева поведінки */
typedef struct {
    bt_node_t nodes[BT_MAX_NODES];
    uint8_t node_count;
    uint8_t root_id;
    blackboard_t bb;
} bt_tree_t;

/* === РОБОТА З ДОШКОЮ ОГОЛОШЕНЬ === */

void bb_init(blackboard_t *bb) {
    memset(bb, 0, sizeof(blackboard_t));
}

bool bb_set_float(blackboard_t *bb, const char *key, float val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            bb->entries[i].type = BB_TYPE_FLOAT;
            bb->entries[i].data.f_val = val;
            bb->entries[i].is_set = true;
            return true;
        }
    }
    if (bb->count >= BT_MAX_BB_ENTRIES) return false;
    strncpy(bb->entries[bb->count].key, key, BT_KEY_LEN - 1);
    bb->entries[bb->count].key[BT_KEY_LEN - 1] = '\0';
    bb->entries[bb->count].type = BB_TYPE_FLOAT;
    bb->entries[bb->count].data.f_val = val;
    bb->entries[bb->count].is_set = true;
    bb->count++;
    return true;
}

bool bb_get_float(const blackboard_t *bb, const char *key, float *out_val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (bb->entries[i].is_set && strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            if (bb->entries[i].type == BB_TYPE_FLOAT) {
                *out_val = bb->entries[i].data.f_val;
                return true;
            }
        }
    }
    return false;
}

bool bb_set_bool(blackboard_t *bb, const char *key, bool val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            bb->entries[i].type = BB_TYPE_BOOL;
            bb->entries[i].data.b_val = val;
            bb->entries[i].is_set = true;
            return true;
        }
    }
    if (bb->count >= BT_MAX_BB_ENTRIES) return false;
    strncpy(bb->entries[bb->count].key, key, BT_KEY_LEN - 1);
    bb->entries[bb->count].key[BT_KEY_LEN - 1] = '\0';
    bb->entries[bb->count].type = BB_TYPE_BOOL;
    bb->entries[bb->count].data.b_val = val;
    bb->entries[bb->count].is_set = true;
    bb->count++;
    return true;
}

bool bb_get_bool(const blackboard_t *bb, const char *key, bool *out_val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (bb->entries[i].is_set && strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            if (bb->entries[i].type == BB_TYPE_BOOL) {
                *out_val = bb->entries[i].data.b_val;
                return true;
            }
        }
    }
    return false;
}

/* === СТВОРЕННЯ ТА КОМПОЗИЦІЯ ДЕРЕВА === */

void bt_tree_init(bt_tree_t *tree) {
    memset(tree, 0, sizeof(bt_tree_t));
    bb_init(&tree->bb);
}

uint8_t bt_create_node(bt_tree_t *tree, bt_node_type_t type, bt_tick_fn tick, bt_halt_fn halt) {
    if (tree->node_count >= BT_MAX_NODES) return 0xFF;
    uint8_t id = tree->node_count++;
    bt_node_t *n = &tree->nodes[id];
    n->id = id;
    n->type = type;
    n->status = BT_STATUS_IDLE;
    n->tick_fn = tick;
    n->halt_fn = halt;
    n->child_count = 0;
    n->running_child_idx = 0;
    n->threshold_m = 1;
    n->timeout_ticks = 0;
    n->elapsed_ticks = 0;
    n->user_data = NULL;
    return id;
}

bool bt_add_child(bt_tree_t *tree, uint8_t parent_id, uint8_t child_id) {
    if (parent_id >= tree->node_count || child_id >= tree->node_count) return false;
    bt_node_t *p = &tree->nodes[parent_id];
    if (p->child_count >= BT_MAX_CHILDREN) return false;
    p->children[p->child_count++] = child_id;
    return true;
}

/* === МЕХАНІЗМ ПЕРЕРИВАННЯ ТА ВИКОНАННЯ ТАКТУ === */

void bt_halt_node(bt_tree_t *tree, uint8_t node_id) {
    if (node_id >= tree->node_count) return;
    bt_node_t *n = &tree->nodes[node_id];

    if (n->status == BT_STATUS_RUNNING) {
        if (n->halt_fn) {
            n->halt_fn(n, &tree->bb);
        }
        for (uint8_t i = 0; i < n->child_count; i++) {
            bt_halt_node(tree, n->children[i]);
        }
        n->status = BT_STATUS_IDLE;
        n->running_child_idx = 0;
        n->elapsed_ticks = 0;
    }
}

bt_status_t bt_tick_node(bt_tree_t *tree, uint8_t node_id) {
    if (node_id >= tree->node_count) return BT_STATUS_FAILURE;
    bt_node_t *n = &tree->nodes[node_id];

    switch (n->type) {
        case BT_NODE_ACTION:
        case BT_NODE_CONDITION:
            if (n->tick_fn) {
                n->status = n->tick_fn(n, &tree->bb);
            } else {
                n->status = BT_STATUS_FAILURE;
            }
            return n->status;

        case BT_NODE_SEQUENCE: {
            for (uint8_t i = n->running_child_idx; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_RUNNING) {
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
                if (s == BT_STATUS_FAILURE) {
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_FAILURE;
                    return BT_STATUS_FAILURE;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_SUCCESS;
            return BT_STATUS_SUCCESS;
        }

        case BT_NODE_REACTIVE_SEQUENCE: {
            for (uint8_t i = 0; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_FAILURE) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx > i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_FAILURE;
                    return BT_STATUS_FAILURE;
                }
                if (s == BT_STATUS_RUNNING) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx != i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_SUCCESS;
            return BT_STATUS_SUCCESS;
        }

        case BT_NODE_FALLBACK: {
            for (uint8_t i = n->running_child_idx; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_RUNNING) {
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
                if (s == BT_STATUS_SUCCESS) {
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_SUCCESS;
                    return BT_STATUS_SUCCESS;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_FAILURE;
            return BT_STATUS_FAILURE;
        }

        case BT_NODE_REACTIVE_FALLBACK: {
            for (uint8_t i = 0; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);

                if (s == BT_STATUS_RUNNING) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx > i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
                if (s == BT_STATUS_SUCCESS) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx != i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_SUCCESS;
                    return BT_STATUS_SUCCESS;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_FAILURE;
            return BT_STATUS_FAILURE;
        }

        case BT_NODE_PARALLEL_M_OF_N: {
            uint8_t success_cnt = 0;
            uint8_t failure_cnt = 0;

            for (uint8_t i = 0; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_SUCCESS) success_cnt++;
                else if (s == BT_STATUS_FAILURE) failure_cnt++;
            }

            if (success_cnt >= n->threshold_m) {
                for (uint8_t i = 0; i < n->child_count; i++) {
                    bt_halt_node(tree, n->children[i]);
                }
                n->status = BT_STATUS_SUCCESS;
                return BT_STATUS_SUCCESS;
            }

            if (failure_cnt > (n->child_count - n->threshold_m)) {
                for (uint8_t i = 0; i < n->child_count; i++) {
                    bt_halt_node(tree, n->children[i]);
                }
                n->status = BT_STATUS_FAILURE;
                return BT_STATUS_FAILURE;
            }

            n->status = BT_STATUS_RUNNING;
            return BT_STATUS_RUNNING;
        }

        case BT_NODE_INVERTER: {
            if (n->child_count == 0) return BT_STATUS_FAILURE;
            bt_status_t s = bt_tick_node(tree, n->children[0]);
            if (s == BT_STATUS_SUCCESS) n->status = BT_STATUS_FAILURE;
            else if (s == BT_STATUS_FAILURE) n->status = BT_STATUS_SUCCESS;
            else n->status = s;
            return n->status;
        }

        case BT_NODE_TIMEOUT: {
            if (n->child_count == 0) return BT_STATUS_FAILURE;
            n->elapsed_ticks++;
            if (n->timeout_ticks > 0 && n->elapsed_ticks > n->timeout_ticks) {
                bt_halt_node(tree, n->children[0]);
                n->elapsed_ticks = 0;
                n->status = BT_STATUS_FAILURE;
                return BT_STATUS_FAILURE;
            }
            bt_status_t s = bt_tick_node(tree, n->children[0]);
            if (s != BT_STATUS_RUNNING) {
                n->elapsed_ticks = 0;
            }
            n->status = s;
            return s;
        }

        default:
            return BT_STATUS_FAILURE;
    }
}

bt_status_t bt_tick(bt_tree_t *tree) {
    return bt_tick_node(tree, tree->root_id);
}
