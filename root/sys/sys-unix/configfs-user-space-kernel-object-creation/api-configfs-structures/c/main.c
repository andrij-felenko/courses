struct config_item {
    char                    *ci_name;
    char                    ci_namebuf[CONFIGFS_ITEM_NAME_LEN];
    struct kref             ci_kref;
    struct list_head        ci_entry;
    struct config_item      *ci_parent;
    struct config_group     *ci_group;
    const struct config_item_type *ci_type;
    struct dentry           *ci_dentry;
};
