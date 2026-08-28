static const struct of_device_id vmgenid_of_ids[] = {
	{ .compatible = "microsoft,vmgenid", },
	{ },
};

static const struct acpi_device_id vmgenid_acpi_ids[] = {
	{ "VMGENCTR", 0 },
	{ "VM_GEN_COUNTER", 0 },
	{ }
};
