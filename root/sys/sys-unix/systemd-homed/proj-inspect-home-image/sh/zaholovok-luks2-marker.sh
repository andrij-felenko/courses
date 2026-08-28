$ sudo cryptsetup luksDump /dev/loop7p1
LUKS header information
Version:       	2
UUID:          	7c0a2f5e-1d84-4b1a-9f3c-2ae6d0b47f11
Label:         	andrij
Subsystem:     	(no subsystem)

Data segments:
  0: crypt
	offset: 16777216 [bytes]
	length: (whole device)
	cipher: aes-xts-plain64
	sector: 512 [bytes]

Keyslots:
  0: luks2
	Key:        512 bits
	PBKDF:      argon2id
	Time cost:  4
	Memory:     1048576
	Threads:    4
Tokens:
  0: systemd-homed
Digests:
  0: pbkdf2
