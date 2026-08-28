bool OWFirst(void)                 /* почати пошук спочатку */
{
    LastDiscrepancy = 0;
    LastDeviceFlag = false;
    LastFamilyDiscrepancy = 0;
    return OWSearch();
}

bool OWNext(void)                  /* наступний пристрій; стан лишається від минулого */
{
    return OWSearch();
}

/* Перелічити все, що висить на шині. Повертає кількість знайдених. */
int OWEnumerate(uint8_t addr[][8], int max)
{
    int count = 0;
    for (bool ok = OWFirst(); ok && count < max; ok = OWNext()) {
        /* CRC кожної адреси вже перевірено всередині OWSearch */
        for (int i = 0; i < 8; i++)
            addr[count][i] = ROM_NO[i];   /* зберегти: ROM_NO наступний прохід перепише */
        count++;
    }
    return count;                          /* 0 — шина порожня */
}
