#ifdef CONFIG_PCI
	pci_init();
#endif
#ifdef CONFIG_SBUS
	sbus_init();
#endif
#ifdef CONFIG_MCA
	mca_init();
#endif
#ifdef CONFIG_ZORRO
	zorro_init();
#endif
