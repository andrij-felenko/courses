static int wmi_bus_match(struct device *dev, struct device_driver *drv)
{
    struct wmi_driver *wdrv = to_wmi_driver(drv);
    struct wmi_device *wdev = to_wmi_device(dev);
    const struct wmi_device_id *id;

    id = wdrv->id_table;
    if (!id) return 0;

    while (id->guid_string[0]) {
        if (sysfs_streq(id->guid_string, wdev->guid_string))
            return 1;
        id++;
    }
    return 0;
}
