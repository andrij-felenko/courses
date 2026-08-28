sudo mkdir -p /boot/efi/EFI/hello
sudo cp hello.efi /boot/efi/EFI/hello/
echo 'кілька байтів тексту' | sudo tee /boot/efi/EFI/hello/note.txt >/dev/null

# спосіб 1: іменований запис у незалежній пам'яті прошивки
sudo efibootmgr -c -d /dev/nvme0n1 -p 1 -L "hello" -l '\EFI\hello\hello.efi'

# спосіб 2: нічого не реєструвати — покласти під наперед відомим іменем,
# яке прошивка пробує сама, коли записів про цей носій немає
sudo cp hello.efi /boot/efi/EFI/BOOT/BOOTX64.EFI
