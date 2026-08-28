$ setfacl -m u:hanna:rw report.csv
$ chmod g-w report.csv
$ getfattr -n system.posix_acl_access --only-values report.csv | xxd
00000000: 0200 0000 0100 0600 ffff ffff 0200 0600  ................
00000010: e903 0000 0400 0400 ffff ffff 1000 0400  ................
00000020: ffff ffff 2000 0000 ffff ffff            .... .......

$ ./aclcat -x report.csv
# file: report.csv
# owner: bohdan
# group: staff
01 00 06 00 ff ff ff ff  user::rw-
02 00 06 00 e9 03 00 00  user:hanna:rw-	#effective:r--
04 00 04 00 ff ff ff ff  group::r--
10 00 04 00 ff ff ff ff  mask::r--
20 00 00 00 ff ff ff ff  other::---
