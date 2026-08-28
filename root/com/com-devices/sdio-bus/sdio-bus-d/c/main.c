static const struct sdio_device_id brcmf_sdio_ids[] = {
    { SDIO_DEVICE(SDIO_VENDOR_ID_BROADCOM, SDIO_DEVICE_ID_BROADCOM_43430) },
    { SDIO_DEVICE(SDIO_VENDOR_ID_CYPRESS,  SDIO_DEVICE_ID_CYPRESS_43455)  },
    { /* кінцевий нульовий елемент */ }
};
MODULE_DEVICE_TABLE(sdio, brcmf_sdio_ids);

static struct sdio_driver brcmf_sdiod_driver = {
    .name     = "brcmfmac",
    .id_table = brcmf_sdio_ids,
    .probe    = brcmf_sdiod_probe,
    .remove   = brcmf_sdiod_remove,
};
