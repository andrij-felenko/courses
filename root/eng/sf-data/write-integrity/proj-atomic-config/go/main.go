package config

import "encoding/binary"

const (
    slotAAddr = 0x9000 // окремий сектор під слот A
    slotBAddr = 0xA000 // окремий сектор під слот B (інший сектор!)
)

// footer — підпис, що РОБИТЬ слот дійсним; пишеться ОСТАННІМ, цілим коротким записом
type footer struct {
    version uint32 // лічильник; більший = новіший
    crc     uint32 // CRC від payload, рахується перед записом
}

const footerSize = 8

// дані лежать на початку сектора, підпис — у його кінці
const footerOffset = sectorSize - footerSize

// slotVersion повертає версію дійсного слота, або 0, якщо слот недійсний
func slotVersion(base uint32) uint32 {
    buf := flashRead(base+footerOffset, footerSize)
    version := binary.LittleEndian.Uint32(buf[0:4])
    crc := binary.LittleEndian.Uint32(buf[4:8])
    payload := flashRead(base, configSize)
    if crc32(payload) == crc {
        return version
    }
    return 0
}

func saveConfig(cfg *Config) {
    va := slotVersion(slotAAddr)
    vb := slotVersion(slotBAddr)

    // пишемо в СТАРІШИЙ слот; новій копії — версія на 1 більша за найбільшу
    target := uint32(slotAAddr)
    if va > vb {
        target = slotBAddr
    }
    next := max(va, vb) + 1

    payload := packConfig(cfg)
    flashEraseSector(target)      // 1) стерти (усі біти в 1)
    flashWrite(target, payload)   // 2) записати дані

    buf := make([]byte, footerSize)
    binary.LittleEndian.PutUint32(buf[0:4], next)
    binary.LittleEndian.PutUint32(buf[4:8], crc32(payload))
    flashWrite(target+footerOffset, buf) // 3) підпис — ОСТАННІМ
}
