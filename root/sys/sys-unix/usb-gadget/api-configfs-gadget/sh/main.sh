cd /sys/kernel/config/usb_gadget/g1

echo "" > UDC                       # 1. відв'язати від контролера
rm os_desc/c.1                      # 2. зняти посилання: спершу на конфігурацію…
rm configs/c.1/acm.usb0             #    …далі на функції
rm configs/c.1/ecm.usb0
rmdir configs/c.1/strings/0x409     # 3. рядки конфігурацій
rmdir configs/c.1                   # 4. самі конфігурації
rmdir functions/acm.usb0            # 5. функції
rmdir functions/ecm.usb0
rmdir strings/0x409                 # 6. рядки гаджета
cd .. && rmdir g1                   # 7. гаджет
