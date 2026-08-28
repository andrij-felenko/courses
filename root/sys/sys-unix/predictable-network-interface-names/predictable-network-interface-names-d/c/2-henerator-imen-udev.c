/* Логіка обчислення кандидатів імен у systemd */
int dev_to_net_names(sd_device *dev, NetNames *names) {
    /* 1. Пошук вбудованих індексів прошивки (ACPI / SMBIOS Type 41) */
    names_onboard(dev, names);

    /* 2. Пошук слотів гарячої заміни PCI Express (PCI Hotplug) */
    names_slot(dev, names);

    /* 3. Обчислення топологічного шляху шини (PCI / USB / CCW) */
    names_path(dev, names);

    /* 4. Отримання глобально адміністрованої MAC-адреси */
    names_mac(dev, names);

    return 0;
}
