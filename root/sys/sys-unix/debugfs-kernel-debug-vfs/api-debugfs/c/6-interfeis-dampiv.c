struct debugfs_reg32 {
    char *name;
    unsigned long offset;
};

struct debugfs_regset32 {
    const struct debugfs_reg32 *regs;
    int nregs;
    void __iomem *base;
    struct device *dev;
};

void debugfs_create_regset32(const char *name, umode_t mode,
                            struct dentry *parent,
                            struct debugfs_regset32 *regset);
