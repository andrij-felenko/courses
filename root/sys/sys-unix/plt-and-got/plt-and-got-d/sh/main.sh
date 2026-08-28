$ objdump -d -j .plt /bin/ls

0000000000001020 <.plt>:
    1020:	ff 35 e2 2f 00 00    	push   0x2fe2(%rip)        # GOT[1] (link_map)
    1026:	ff 25 e4 2f 00 00    	jmp    *0x2fe4(%rip)        # GOT[2] (resolver)
    102c:	0f 1f 40 00          	nopl   0x0(%rax)

0000000000001030 <free@plt>:
    1030:	endbr64
    1034:	ff 25 e2 2f 00 00    	jmp    *0x2fe2(%rip)        # GOT[free]
    103a:	68 00 00 00 00       	push   0x0
    103f:	e9 e0 ff ff ff       	jmp    1020 <.plt>
