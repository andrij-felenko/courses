# Збірка атомарного UKI з вбудованим initramfs та параметрами ядра
systemd-ukify build \
    --linux=/boot/vmlinuz-6.10.3-200.fc40.x86_64 \
    --initrd=/boot/initramfs-6.10.3-200.fc40.x86_64.img \
    --cmdline="root=UUID=8f3c1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b ro quiet" \
    --os-release=@/etc/os-release \
    --sbat=@/usr/share/sbat/sbat.csv \
    --uname="6.10.3-200.fc40.x86_64" \
    --stub=/usr/lib/systemd/boot/efi/linuxx64.efi.stub \
    --output=/boot/efi/EFI/Linux/fedora-6.10.3.efi
