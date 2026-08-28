# хто зайняв фізичний діапазон — дерево struct resource
$ sudo grep -i myeth /proc/iomem
  e0001000-e0001fff : e0001000.ethernet

# де це відображення живе у віртуальних адресах ядра
$ sudo grep ioremap /proc/vmallocinfo
0xffff800010800000-0xffff800010802000   8192 devm_ioremap_resource+0x54/0xd0 \
  phys=0x00000000e0001000 ioremap

# лічильник входів у обробник, по одному стовпцю на ядро процесора
$ grep myeth /proc/interrupts
 41:       1024          0     GICv3  62 Level     e0001000.ethernet
