$ sudo rmmod stend && sudo insmod stend.ko zlamaty=1
$ echo devres-stend | sudo tee /sys/bus/platform/drivers/devres-stend/unbind
$ dmesg | tail -20
devres-stend devres-stend: remove(): почав
==================================================================
BUG: KASAN: slab-use-after-free in stend_robota+0x44/0xb0 [stend]
Write of size 4 at addr ffff888104c1a800 by task kworker/2:1/58
...
Freed by task 1874:
 kfree+0x...
 stend_remove+0x38/0x70 [stend]
