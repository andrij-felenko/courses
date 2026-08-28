#include <linux/mmc/sdio_func.h>
#include <linux/mmc/sdio_ids.h>

static const struct sdio_device_id my_sdio_ids[] = {
    { SDIO_DEVICE(0x02d0, 0xa9a6) }, /* Broadcom BCM43438 Wi-Fi */
    { SDIO_DEVICE_CLASS(SDIO_CLASS_WLAN) }, /* Будь-який стандартний Wi-Fi */
    { /* кінець таблиці */ }
};
MODULE_DEVICE_TABLE(sdio, my_sdio_ids);

static struct sdio_driver my_sdio_driver = {
    .name     = "my_sdio_wlan",
    .id_table = my_sdio_ids,
    .probe    = my_sdio_probe,
    .remove   = my_sdio_remove,
    .drv = {
        .owner = THIS_MODULE,
    },
};
