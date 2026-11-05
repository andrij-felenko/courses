// Статична реалізація вузла для BT на C
typedef enum {
    BT_SUCCESS,
    BT_FAILURE,
    BT_RUNNING
} BtStatus;

typedef BtStatus (*BtTickFunc)(void* context);

typedef struct BtNode {
    BtTickFunc tick;
    struct BtNode* children;
    uint8_t num_children;
} BtNode;

// Приклад вузла-селектора
BtStatus tick_selector(void* context, BtNode* node) {
    for (uint8_t i = 0; i < node->num_children; i++) {
        BtStatus status = node->children[i].tick(context);
        if (status != BT_FAILURE) {
            return status;
        }
    }
    return BT_FAILURE;
}
