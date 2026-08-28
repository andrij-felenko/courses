static const struct regmap_irq pmic_irqs[] = {
	[PMIC_IRQ_BUCK1_OC]  = { .mask = BIT(0), .reg_offset = 0 },
	[PMIC_IRQ_BAT_LOW]   = { .mask = BIT(1), .reg_offset = 0 },
	[PMIC_IRQ_PWRKEY]    = { .mask = BIT(2), .reg_offset = 0 },
	[PMIC_IRQ_RTC_ALARM] = { .mask = BIT(0), .reg_offset = 1 },
	[PMIC_IRQ_TEMP_WARN] = { .mask = BIT(1), .reg_offset = 1 },
};

static const struct regmap_irq_chip pmic_irq_chip = {
	.name        = "pmic-irq-chip",
	.status_base = PMIC_REG_INT_STATUS1,
	.mask_base   = PMIC_REG_INT_MASK1,
	.ack_base    = PMIC_REG_INT_STATUS1, /* Write-1-to-Clear */
	.num_regs    = 2,
	.irqs        = pmic_irqs,
	.num_irqs    = ARRAY_SIZE(pmic_irqs),
};
