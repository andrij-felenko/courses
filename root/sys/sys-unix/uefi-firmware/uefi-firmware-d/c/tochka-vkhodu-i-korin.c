EFI_STATUS EFIAPI efi_main(EFI_HANDLE image, EFI_SYSTEM_TABLE *st)
{
        EFI_GUID gop_guid = EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
        EFI_GRAPHICS_OUTPUT_PROTOCOL *gop;

        st->ConOut->OutputString(st->ConOut, L"жива\r\n");

        /* прошивка завела сторожовий таймер на 5 хвилин, перш ніж нас запустити:
           не вимкнеш — довге читання з повільного диска обірветься перезавантаженням */
        st->BootServices->SetWatchdogTimer(0, 0, 0, NULL);

        if (st->BootServices->LocateProtocol(&gop_guid, NULL, (void **)&gop) == EFI_SUCCESS)
                st->ConOut->OutputString(st->ConOut, L"кадровий буфер є\r\n");

        return EFI_SUCCESS;     /* повернення = вихід із програми */
}
