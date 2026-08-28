#include <linux/input/sparse-keymap.h>

static const struct key_entry my_wmi_keymap[] = {
    { KE_KEY, 0x85, { KEY_BRIGHTNESSUP } },
    { KE_KEY, 0x86, { KEY_BRIGHTNESSDOWN } },
    { KE_KEY, 0x87, { KEY_WLAN } },
    { KE_END, 0 }
};

/* У функції .probe(): */
int ret = sparse_keymap_setup(priv->input_dev, my_wmi_keymap, NULL);

/* У функції .notify(): */
if (data && data->type == ACPI_TYPE_INTEGER)
    sparse_keymap_report_event(priv->input_dev, (u32)data->integer.value, 1, true);
