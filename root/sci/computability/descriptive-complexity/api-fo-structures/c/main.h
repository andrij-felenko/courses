/* =========================================================================
 * 1. УПРАВЛІННЯ РЕЛЯЦІЙНИМИ СТРУКТУРАМИ ТА AST-ВУЗЛАМИ У C
 * ========================================================================= */

typedef struct {
    char name[32];
    size_t arity;
    size_t capacity;
    size_t tuple_count;
    size_t *tuples;
} FORelation;

typedef struct {
    size_t domain_size;
    size_t relation_count;
    FORelation *relations;
    bool has_order;
} FOStructure;

typedef struct FONode {
    uint8_t type;
    int var_id;
    int var_id2;
    size_t relation_idx;
    struct FONode *left;
    struct FONode *right;
} FONode;

typedef struct {
    size_t bindings[64];
    bool is_bound[64];
} FOEnvironment;

FOStructure* fo_structure_create(size_t domain_size, bool has_order);
int fo_structure_add_relation(FOStructure *struct_ptr, const char *name, size_t arity);
bool fo_relation_add_tuple(FOStructure *struct_ptr, size_t relation_idx, const size_t *tuple);
void fo_structure_free(FOStructure *struct_ptr);

FONode* fo_node_create_rel(size_t relation_idx, int var1, int var2);
FONode* fo_node_create_eq(int var1, int var2);
FONode* fo_node_create_lt(int var1, int var2);
FONode* fo_node_create_not(FONode *child);
FONode* fo_node_create_and(FONode *left, FONode *right);
FONode* fo_node_create_or(FONode *left, FONode *right);
FONode* fo_node_create_exists(int var_id, FONode *body);
FONode* fo_node_create_forall(int var_id, FONode *body);
void fo_node_free(FONode *node);

bool fo_evaluate(const FONode *node, const FOStructure *struct_ptr, FOEnvironment *env);
