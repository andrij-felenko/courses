package wearleveling

import "encoding/binary"

// Кільце з N секторів; у кожному — один запис {seq, value, crc}.
// «Жива» комірка та, у якої найбільший seq; писати треба в наступну за нею.
const (
	nSect    = 64   // скільки секторів ділять знос
	sectSize = 4096 // розмір сектора Flash, байтів
	magic    = 0xC0FFEE
	recSize  = 16 // один слот = magic, seq, value, crc — чотири uint32
)

// апаратура застабована ззовні: flashRead/flashWrite/flashEraseSector, crc32

type Counter struct {
	base uint32
	seq  uint32 // seq останнього запису
	slot uint32 // індекс сектора з останнім записом
}

// Знайти найсвіжіший запис серед усіх секторів (виклик раз, на старті).
func (c *Counter) Mount() (found bool, value uint32) {
	var bestSeq uint32
	for i := uint32(0); i < nSect; i++ {
		r := flashRead(c.base+i*sectSize, recSize)
		if binary.LittleEndian.Uint32(r[0:]) != magic { // порожній/стертий сектор
			continue
		}
		if crc32(r[:recSize-4]) != binary.LittleEndian.Uint32(r[12:]) { // битий запис — пропустити
			continue
		}
		if seq := binary.LittleEndian.Uint32(r[4:]); !found || seq > bestSeq { // запам'ятати найсвіжіший
			bestSeq, c.slot, value, found = seq, i, binary.LittleEndian.Uint32(r[8:]), true
		}
	}
	if found {
		c.seq = bestSeq
	} else {
		c.seq = 0
	}
	return found, value
}

// Записати нове значення — у НАСТУПНИЙ сектор по колу (ось і все вирівнювання).
func (c *Counter) Save(value uint32) {
	next := (c.slot + 1) % nSect     // ротація: наступний сектор
	addr := c.base + next*sectSize
	flashEraseSector(addr)           // одне стирання раз на оберт
	var r [recSize]byte
	binary.LittleEndian.PutUint32(r[0:], magic)
	binary.LittleEndian.PutUint32(r[4:], c.seq+1) // новий seq — на одиницю більший
	binary.LittleEndian.PutUint32(r[8:], value)
	binary.LittleEndian.PutUint32(r[12:], crc32(r[:recSize-4]))
	flashWrite(addr, r[:])           // дописуємо у вільну комірку
	c.slot, c.seq = next, c.seq+1    // тепер «жива» комірка — ця
}
