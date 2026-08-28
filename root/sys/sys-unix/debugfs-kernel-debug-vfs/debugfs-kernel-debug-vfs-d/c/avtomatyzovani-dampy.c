struct debugfs_reg32 my_registers[] = {
    { .name = "CTRL_REG",  .offset = 0x00 },
    { .name = "STATUS_REG",.offset = 0x04 },
    { .name = "DATA_REG",  .offset = 0x08 },
};

struct debugfs_regset32 my_regset = {
    .regs  = my_registers,
    .nregs = ARRAY_SIZE(my_registers),
    .base  = io_memory_base_address,
};

/* Створення файлу regset у debugfs */
debugfs_create_regset32("regdump", 0444, dir_dentry, &my_regset);
