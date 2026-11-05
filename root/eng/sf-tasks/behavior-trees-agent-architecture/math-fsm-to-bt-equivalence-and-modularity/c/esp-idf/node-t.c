typedef enum { STATUS_SUCCESS, STATUS_FAILURE, STATUS_RUNNING } status_t;

typedef struct node_t {
    status_t (*tick)(struct node_t* self);
} node_t;

typedef struct {
    node_t base;
    node_t** children;
    size_t child_count;
} selector_t;

status_t selector_tick(node_t* self) {
    selector_t* selector = (selector_t*)self;
    for (size_t i = 0; i < selector->child_count; ++i) {
        status_t s = selector->children[i]->tick(selector->children[i]);
        if (s != STATUS_FAILURE) {
            return s;
        }
    }
    return STATUS_FAILURE;
}
