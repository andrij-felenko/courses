// FatFs кличе цю функцію зі своїми типами: drv — номер носія,
// buff — куди класти дані, sector — номер сектора, count — скільки їх.
DRESULT disk_read(BYTE drv, BYTE *buff, LBA_t sector, UINT count) {
    if (drv != 0) {
        return RES_PARERR;            // у нас лише носій 0
    }
    // прочитати count секторів по 512 байтів, починаючи із sector
    for (UINT i = 0; i < count; i++) {
        if (sd_read_block(sector + i, buff + i * 512) != 0) {
            return RES_ERROR;         // фізичне читання не вдалося
        }
    }
    return RES_OK;                    // усе прочитано
}
