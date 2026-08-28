enum of_reconfig_change_action {
    OF_RECONFIG_ATTACH_NODE,    /* Приєднання нового вузла до дерева */
    OF_RECONFIG_DETACH_NODE,    /* Від'єднання вузла від дерева */
    OF_RECONFIG_ADD_PROPERTY,   /* Додавання нової властивості */
    OF_RECONFIG_REMOVE_PROPERTY,/* Видалення властивості */
    OF_RECONFIG_UPDATE_PROPERTY /* Оновлення вмісту властивості */
};

struct of_changeset_entry {
    struct list_head node;
    enum of_reconfig_change_action action;
    struct device_node *np;
    struct property *prop;
    struct property *old_prop;
};

struct of_changeset {
    struct list_head entries;   /* Двобічно зв'язаний список журнальованих дій */
};
