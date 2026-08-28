import struct

SLOT_A_ADDR = 0x9000     # окремий сектор під слот A
SLOT_B_ADDR = 0xA000     # окремий сектор під слот B (інший сектор!)

# підпис, що РОБИТЬ слот дійсним: version, crc — два uint32
# пишеться ОСТАННІМ, цілим коротким записом
FOOTER_FMT = "<II"                        # version (лічильник), crc від payload
FOOTER_SIZE = struct.calcsize(FOOTER_FMT)

# дані лежать на початку сектора, підпис — у його кінці
FOOTER_OFFSET = SECTOR_SIZE - FOOTER_SIZE

def slot_version(base):
    """Версія дійсного слота, або 0, якщо слот недійсний."""
    version, crc = struct.unpack(FOOTER_FMT, flash_read(base + FOOTER_OFFSET, FOOTER_SIZE))
    payload = flash_read(base, CONFIG_SIZE)
    return version if crc32(payload) == crc else 0

def save_config(cfg):
    va = slot_version(SLOT_A_ADDR)
    vb = slot_version(SLOT_B_ADDR)

    # пишемо в СТАРІШИЙ слот; новій копії — версія на 1 більша за найбільшу
    target = SLOT_A_ADDR if va <= vb else SLOT_B_ADDR
    next_v = max(va, vb) + 1

    payload = pack_config(cfg)
    flash_erase_sector(target)                        # 1) стерти (усі біти в 1)
    flash_write(target, payload)                      # 2) записати дані

    footer = struct.pack(FOOTER_FMT, next_v, crc32(payload))
    flash_write(target + FOOTER_OFFSET, footer)       # 3) підпис — ОСТАННІМ
