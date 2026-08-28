// Вузол персистентного дерева на C з лічильником посилань
typedef struct PersistentNode {
    int data;
    struct PersistentNode* left;
    struct PersistentNode* right;
    int ref_count;
} PersistentNode;

PersistentNode* create_persistent_node(int val, PersistentNode* l, PersistentNode* r) {
    PersistentNode* node = (PersistentNode*)malloc(sizeof(PersistentNode));
    node->data = val;
    node->left = l;
    node->right = r;
    node->ref_count = 1;
    if (l) l->ref_count++;
    if (r) r->ref_count++;
    return node;
}
