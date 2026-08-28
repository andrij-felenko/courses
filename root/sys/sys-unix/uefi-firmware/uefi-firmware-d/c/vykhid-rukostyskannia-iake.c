static EFI_STATUS take_over(EFI_HANDLE image, EFI_SYSTEM_TABLE *st)
{
        EFI_BOOT_SERVICES *bs = st->BootServices;
        EFI_MEMORY_DESCRIPTOR *map = NULL;
        UINTN size = 0, key = 0, dsz = 0;
        UINT32 dver;
        EFI_STATUS rc;

        for (;;) {
                rc = bs->GetMemoryMap(&size, map, &key, &dsz, &dver);
                if (rc == EFI_BUFFER_TOO_SMALL) {
                        if (map)
                                bs->FreePool(map);
                        /* запас на описи, які додасть саме це виділення */
                        size += 4 * dsz;
                        rc = bs->AllocatePool(EfiLoaderData, size, (void **)&map);
                        if (rc != EFI_SUCCESS)
                                return rc;
                        continue;
                }
                if (rc != EFI_SUCCESS)
                        return rc;

                rc = bs->ExitBootServices(image, key);
                if (rc == EFI_SUCCESS)
                        return EFI_SUCCESS;             /* машина наша */
                if (rc != EFI_INVALID_PARAMETER)
                        return rc;
                /* ключ застарів: карта змінилася. Нічого не друкуємо
                   й нічого не виділяємо — просто перечитуємо її. */
        }
}
