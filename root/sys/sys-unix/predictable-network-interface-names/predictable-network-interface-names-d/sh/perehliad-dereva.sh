$ udevadm info --attribute-walk --path=/sys/class/net/enp3s0
  looking at device '/devices/pci0000:00/0000:00:1c.4/0000:03:00.0/net/enp3s0':
    KERNEL=="enp3s0"
    SUBSYSTEM=="net"
    ATTR{address}=="78:e7:d1:ea:46:da"
    ATTR{type}=="1"

  looking at parent device '/devices/pci0000:00/0000:00:1c.4/0000:03:00.0':
    KERNELS=="0000:03:00.0"
    SUBSYSTEMS=="pci"
    ATTRS{vendor}=="0x8086"
    ATTRS{device}=="0x1539"
