$ udevadm info --attribute-walk --name=/dev/ttyUSB0
  looking at device '/devices/.../ttyUSB0/tty/ttyUSB0':
    KERNEL=="ttyUSB0"
    SUBSYSTEM=="tty"
  looking at parent device '/devices/.../1-2':
    KERNELS=="1-2"
    SUBSYSTEMS=="usb"
    ATTRS{idVendor}=="0403"
    ATTRS{idProduct}=="6001"
    ATTRS{serial}=="A6008isP"
