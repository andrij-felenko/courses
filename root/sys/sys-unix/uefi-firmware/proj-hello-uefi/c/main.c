#include <efi.h>

/* Імена протоколів — випадкові 128-бітні числа, ніхто ні з ким не домовлявся */
static EFI_GUID li_guid   = {0x5b1b31a1,0x9562,0x11d2,{0x8e,0x3f,0,0xa0,0xc9,0x69,0x72,0x3b}};
static EFI_GUID fs_guid   = {0x964e5b22,0x6459,0x11d2,{0x8e,0x39,0,0xa0,0xc9,0x69,0x72,0x3b}};
static EFI_GUID info_guid = {0x09576e92,0x6d3f,0x11d2,{0x8e,0x39,0,0xa0,0xc9,0x69,0x72,0x3b}};

static EFI_SYSTEM_TABLE *ST;

static void say(const CHAR16 *s)
{
        ST->ConOut->OutputString(ST->ConOut, (CHAR16 *)s);
}

/* printf немає й не буде: десяткове число складаємо руками, одразу в CHAR16 */
static void say_u64(UINT64 v)
{
        CHAR16 buf[21];
        int i = 20;

        buf[i] = L'\0';
        do {
                buf[--i] = (CHAR16)(L'0' + v % 10);
                v /= 10;
        } while (v);
        say(&buf[i]);
}

EFI_STATUS EFIAPI efi_main(EFI_HANDLE image, EFI_SYSTEM_TABLE *st)
{
        EFI_BOOT_SERVICES *bs = st->BootServices;
        EFI_LOADED_IMAGE_PROTOCOL *li;
        EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *fs;
        EFI_FILE_PROTOCOL *root, *file;
        EFI_FILE_INFO *info;
        EFI_STATUS rc;
        UINTN sz = 0;

        ST = st;
        bs->SetWatchdogTimer(0, 0, 0, NULL);    /* перше, що робимо, — знімаємо вирок */
        say(L"привіт із прошивки\r\n");

        rc = bs->HandleProtocol(image, &li_guid, (void **)&li);
        if (rc != EFI_SUCCESS) goto out;        /* хто я і звідки мене взяли */

        rc = bs->HandleProtocol(li->DeviceHandle, &fs_guid, (void **)&fs);
        if (rc != EFI_SUCCESS) goto out;        /* той самий розділ як файлова система */

        rc = fs->OpenVolume(fs, &root);
        if (rc != EFI_SUCCESS) goto out;

        rc = root->Open(root, &file, L"\\EFI\\hello\\note.txt", EFI_FILE_MODE_READ, 0);
        if (rc != EFI_SUCCESS) goto out;

        /* два виклики: спершу питаємо розмір буфера, потім даємо буфер */
        rc = file->GetInfo(file, &info_guid, &sz, NULL);
        if (rc != EFI_BUFFER_TOO_SMALL) { rc = EFI_DEVICE_ERROR; goto out; }
        rc = bs->AllocatePool(EfiLoaderData, sz, (void **)&info);
        if (rc != EFI_SUCCESS) goto out;
        rc = file->GetInfo(file, &info_guid, &sz, info);
        if (rc != EFI_SUCCESS) goto out;

        say(L"розмір файлу: ");
        say_u64(info->FileSize);
        say(L" байтів\r\n");

        bs->FreePool(info);
        file->Close(file);
        root->Close(root);
out:
        if (rc != EFI_SUCCESS)
                say(L"не вдалося\r\n");
        bs->Stall(3 * 1000 * 1000);             /* 3 секунди, щоб устигнути прочитати */
        return rc;
}
