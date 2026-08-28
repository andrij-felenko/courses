// нулі в хвості — де Брейн: виділити молодший біт можна за дві операції
const deBruijn64 = 0x03f79d71b4ca8b09

func TrailingZeros64(x uint64) int {
	if x == 0 {
		return 64
	}
	return int(deBruijn64tab[(x&-x)*deBruijn64>>(64-6)])
}

// довжина числа — розгорнутий цикл і таблиця на байт: жодного де Брейна
func Len64(x uint64) (n int) {
	if x >= 1<<32 {
		x >>= 32
		n = 32
	}
	if x >= 1<<16 {
		x >>= 16
		n += 16
	}
	if x >= 1<<8 {
		x >>= 8
		n += 8
	}
	return n + int(len8tab[x])
}
