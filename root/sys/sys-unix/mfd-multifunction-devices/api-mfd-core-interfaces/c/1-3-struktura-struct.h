struct regmap_irq_chip {
	const char *name;
	unsigned int status_base;
	unsigned int mask_base;
	unsigned int unmask_base;
	unsigned int ack_base;
	unsigned int wake_base;
	unsigned int type_base;
	bool mask_writeonly;
	bool mask_invert;
	bool clear_on_unmask;
	bool ack_invert;
	bool runtime_pm;
	int num_regs;
	const struct regmap_irq *irqs;
	int num_irqs;
	int num_type_reg;
	int (*handle_pre_irq)(void *irq_drv_data);
	int (*handle_post_irq)(void *irq_drv_data);
	int (*set_type_config)(unsigned int **buf, unsigned int type,
			       const struct regmap_irq *irq_data, int idx,
			       void *irq_drv_data);
};
