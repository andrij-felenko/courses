typedef struct node { int key; int refs; struct node* kid[2]; } node;

/* Зібрати новий вузол шляху: копія old, у якій дитина `which` замінена на
   свіжу new_child, а протилежна дитина лишається СПІЛЬНОЮ зі старою версією. */
node* copy_path_node(node* old, int which, node* new_child) {
    node* c = malloc(sizeof(node));
    c->refs = 1;                        /* новий вузол поки лише наш */
    c->key  = old->key;
    c->kid[which]  = new_child;         /* туди, куди пішов запис */
    c->kid[!which] = old->kid[!which];  /* убік — той самий покажчик: спільне */
    if (c->kid[!which]) c->kid[!which]->refs++;   /* прийняли спільне піддерево */
    return c;                           /* O(1) роботи на один вузол шляху */
}
