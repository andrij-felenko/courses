struct kernfs_node {
    atomic_t            count;
    atomic_t            active;
    struct kernfs_node  *parent;
    const char          *name;
    struct rb_node      rb;
    const void          *ns;
    unsigned int        hash;
    union {                              /* безіменна: kn->dir, kn->attr, kn->symlink */
        struct kernfs_elem_dir      dir;
        struct kernfs_elem_symlink  symlink;
        struct kernfs_elem_attr     attr;
    };
    void                *priv;
    union kernfs_node_id id;
    unsigned short      flags;
    umode_t             mode;
    struct kernfs_iattrs *iattr;
};
