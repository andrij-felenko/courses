struct klp_func {
        const char *old_name;      /* заповнює автор */
        void *new_func;            /* заповнює автор */
        unsigned long old_sympos;  /* заповнює автор, необов'язково */
        /* далі — службові: old_func, kobj, node, stack_node,
           old_size, new_size, nop, patched, transition */
};

struct klp_object {
        const char *name;
        struct klp_func *funcs;
        struct klp_callbacks callbacks;
        /* службові: kobj, func_list, node, mod, dynamic, patched */
};

struct klp_patch {
        struct module *mod;
        struct klp_object *objs;
        struct klp_state *states;
        bool replace;
        /* службові: list, kobj, obj_list, enabled, forced, free_work, finish */
};
