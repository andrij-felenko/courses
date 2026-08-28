const (
	sync   = 0xAA
	maxLen = 32
)

type state int

const (
	waitSync state = iota
	getLen
	getData
	getCRC
)

// весь стан — у полях; він переживає між викликами Feed()
type Parser struct {
	st       state
	buf      []byte
	length   int
	crc      byte
	onPacket func([]byte)
}

func (p *Parser) Feed(b byte) {
	switch p.st {
	case waitSync:
		if b == sync {
			p.st = getLen // інакше просто ігноруємо
		}
	case getLen:
		if b == 0 || int(b) > maxLen { // захист: 0 або завелика довжина
			p.st = waitSync
			return
		}
		p.length = int(b)
		p.buf = p.buf[:0]
		p.crc = b // CRC накриває й байт довжини
		p.st = getData
	case getData:
		p.buf = append(p.buf, b)
		p.crc ^= b // CRC рахуємо на льоту
		if len(p.buf) == p.length {
			p.st = getCRC
		}
	case getCRC:
		if b == p.crc {
			p.onPacket(p.buf) // цілий пакет — у роботу
		}
		p.st = waitSync // у будь-якому разі — наново
	}
}
