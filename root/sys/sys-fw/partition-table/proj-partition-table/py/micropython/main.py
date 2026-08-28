from esp32 import Partition

def dump_layout():
    # 1) з якого app-розділу нас запустив завантажувач
    run = Partition(Partition.RUNNING)
    _, _, addr, size, label, _ = run.info()
    print("виконуюсь із '%s' @ 0x%06x (%d КБ)" % (label, addr, size // 1024))

    # 2) знайти розділ NVS за типом+підтипом (перший-ліпший)
    found = Partition.find(Partition.TYPE_DATA, subtype=0x02)  # 0x02 = NVS
    if found:
        _, _, addr, size, _, _ = found[0].info()
        end = addr + size                                 # верхня межа розділу
        print("nvs @ 0x%06x..0x%06x" % (addr, end))
