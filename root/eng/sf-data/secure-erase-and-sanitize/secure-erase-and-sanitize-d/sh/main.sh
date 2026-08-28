$ sudo hdparm -I /dev/sda | grep -A7 Security
Security:
        Master password revision code = 65534
                supported
        not     enabled
        not     locked
        not     frozen
                supported: enhanced erase
        2min for SECURITY ERASE UNIT. 2min for ENHANCED SECURITY ERASE UNIT.

$ sudo hdparm --user-master u --security-set-pass p /dev/sda
$ time sudo hdparm --user-master u --security-erase p /dev/sda
