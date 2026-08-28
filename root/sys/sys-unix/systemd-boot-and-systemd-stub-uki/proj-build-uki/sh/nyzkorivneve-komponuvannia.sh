# Крок 1: Створення тимчасового файла командного рядка
echo -n "root=UUID=8f3c1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b ro quiet splash" > /tmp/cmdline.txt

# Крок 2: Ручна додамп секцій у заглушку systemd-stub
objcopy \
    --add-section .osrel=/etc/os-release --change-section-vma .osrel=0x20000 \
    --add-section .cmdline=/tmp/cmdline.txt --change-section-vma .cmdline=0x30000 \
    --add-section .linux=/boot/vmlinuz --change-section-vma .linux=0x40000 \
    --add-section .initrd=/boot/initramfs.img --change-section-vma .initrd=0x3000000 \
    /usr/lib/systemd/boot/efi/linuxx64.efi.stub /tmp/uki-unsigned.efi

# Крок 3: Підпис готового бінарника ключем Secure Boot
sb-sign --key /etc/secureboot/db.key --cert /etc/secureboot/db.crt \
        --output /boot/efi/EFI/Linux/fedora-custom.efi /tmp/uki-unsigned.efi
