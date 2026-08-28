modprobe libcomposite
mount -t configfs none /sys/kernel/config

cd /sys/kernel/config/usb_gadget
mkdir g1 && cd g1

echo 0x1d6b > idVendor      # Linux Foundation
echo 0x0104 > idProduct     # Multifunction Composite Gadget
echo 0x0200 > bcdUSB        # заявляємо USB 2.0

mkdir -p strings/0x409      # 0x409 — англійська (США)
echo "0123456789"        > strings/0x409/serialnumber
echo "Своя майстерня"    > strings/0x409/manufacturer
echo "Пристрій на Linux" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "Порт і мережа" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower          # міліампери

mkdir functions/acm.usb0                 # послідовний порт
mkdir functions/ecm.usb0                 # мережевий інтерфейс

ln -s functions/acm.usb0 configs/c.1/
ln -s functions/ecm.usb0 configs/c.1/

ls /sys/class/udc                        # → fe980000.usb
echo fe980000.usb > UDC                  # ось тут пристрій оживає
