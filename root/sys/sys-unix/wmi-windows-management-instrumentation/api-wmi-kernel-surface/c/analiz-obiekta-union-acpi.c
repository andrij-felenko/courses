static void my_wmi_notify(struct wmi_device *wdev, union acpi_object *data)
{
    struct my_driver_priv *priv = dev_get_drvdata(&wdev->dev);

    if (!data) {
        dev_warn(&wdev->dev, "Отримано порожнє сповіщення WMI\n");
        return;
    }

    switch (data->type) {
    case ACPI_TYPE_INTEGER:
        dev_dbg(&wdev->dev, "Отримано цілочисельну подію WMI: 0x%llx\n",
                data->integer.value);
        my_handle_scancode(priv, (u32)data->integer.value);
        break;

    case ACPI_TYPE_BUFFER:
        dev_dbg(&wdev->dev, "Отримано буфер події WMI довжиною %u байт\n",
                data->buffer.length);
        my_parse_event_buffer(priv, data->buffer.pointer, data->buffer.length);
        break;

    case ACPI_TYPE_PACKAGE:
        dev_dbg(&wdev->dev, "Отримано пакет подій WMI з %u елементів\n",
                data->package.count);
        break;

    default:
        dev_err(&wdev->dev, "Непідтримуваний тип об'єкта події: %u\n", data->type);
        break;
    }
}
