$ sudo cryptsetup open /dev/loop7p1 peek
Enter passphrase for /dev/loop7p1:
$ sudo mount -o ro /dev/mapper/peek /mnt
$ ls /mnt
andrij
$ sudo jq -r '.userName, .realName, .disposition, .lastChangeUSec' /mnt/andrij/.identity
andrij
Andrij Felenko
regular
1754470920045391
