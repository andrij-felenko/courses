### Практика: налаштування vDPA за допомогою `iproute2`

У сучасних ядрах Linux управління підсистемою vDPA інтегровано в набір утиліт `iproute2` (команда `vdpa`).

Щоб подивитися список доступної vDPA-сумісної апаратури (менеджмент-пристроїв):
```bash
$ vdpa mgmtdev show
pci/0000:03:00.2:
  supported_classes net
  max_supported_vqs 3
```

Ім'я менеджмент-пристрою — це його адреса на шині (`pci/0000:03:00.2`). Створення vDPA-пристрою поверх цього обладнання:
```bash
$ vdpa dev add name vdpa0 mgmtdev pci/0000:03:00.2
```

Перегляд створених пристроїв:
```bash
$ vdpa dev show
vdpa0: type network mgmtdev pci/0000:03:00.2 vendor_id 5555 max_vqs 3 max_vq_size 256
```

Після цього пристрій `vdpa0` з'явиться в `/dev/vhost-vdpa-0` (завдяки драйверу `vhost_vdpa`), і ми можемо передати його QEMU як звичайний `vhost` пристрій:
```bash
qemu-system-x86_64 ... \
  -netdev vhost-vdpa,vhostdev=/dev/vhost-vdpa-0,id=net0 \
  -device virtio-net-pci,netdev=net0,page-per-vq=on
```
У цьому прикладі QEMU налаштує пристрій, але вся мережева активність гостя йтиме безпосередньо через PCI-пристрій `0000:03:00.2`, минаючи процесор хоста.
