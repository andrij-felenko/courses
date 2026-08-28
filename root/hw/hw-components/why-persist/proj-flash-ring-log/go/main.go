package ringlog

import "encoding/binary"

const (
	sectorSize = 4096       // розмір сектора Flash (типово 4 КБ)
	nSectors   = 16         // скільки секторів під лог
	emptySeq   = 0xFFFFFFFF // стерте слово = вільний сектор
	payloadLen = sectorSize - 8
)

// --- апаратні примітиви Flash (надає драйвер платформи) ---
// flashRead(sector) []byte       — повертає sectorSize байтів
// flashErase(sector)             — усі біти в 0xFF
// flashWrite(sector, data)       — data рівно sectorSize байтів
// crc32(data) uint32

var (
	head    uint32 // індекс сектора-голови
	nextSeq uint32 // номер для наступного запису
)

// Дописати подію. O(1): майже завжди це лише запис у голову.
func logAppend(event []byte) {
	if len(event) > payloadLen { // не влазить
		return
	}

	ahead := (head + 1) % nSectors // сектор попереду голови
	flashErase(ahead)              // стираємо наперед — губимо найдавніше

	rec := make([]byte, sectorSize)
	for i := range rec { // лишок payload — як стертий
		rec[i] = 0xFF
	}
	seq := nextSeq
	nextSeq++
	copy(rec[8:], event)
	crc := crc32(rec[8:]) // мітка ставиться ОСТАННЬОЮ
	binary.LittleEndian.PutUint32(rec[0:], seq)
	binary.LittleEndian.PutUint32(rec[4:], crc)

	flashWrite(head, rec) // запис у голову
	head = ahead          // голова посунулась по колу
}

// Відновлення при старті: знайти голову й продовжити нумерацію. O(n).
func logInit() {
	var bestSeq, bestIdx uint32
	found := false

	for i := uint32(0); i < nSectors; i++ {
		rec := flashRead(i)
		seq := binary.LittleEndian.Uint32(rec[0:])
		crc := binary.LittleEndian.Uint32(rec[4:])
		payload := rec[8:sectorSize]
		if seq == emptySeq { // вільний — пропустити
			continue
		}
		if crc != crc32(payload) { // обірваний запис —
			continue // мітка не сходиться
		}
		if !found || seq > bestSeq { // шукаємо найбільший №
			bestSeq, bestIdx, found = seq, i, true
		}
	}

	if !found { // чистий Flash: лог іще порожній
		head, nextSeq = 0, 1
	} else { // голова — одразу за найновішим записом
		head = (bestIdx + 1) % nSectors
		nextSeq = bestSeq + 1
	}
}
