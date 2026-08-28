// wire types
const (
	WtVarint = 0
	WtI64    = 1
	WtLen    = 2
	WtI32    = 5
)

// Записати тег поля (номер + тип) у buf; повертає число байтів або 0.
func TagEncode(fieldNum uint32, wireType uint8, buf []byte) int {
	tag := (fieldNum << 3) | uint32(wireType&0x07)
	return VarintEncodeU32(tag, buf) // тег — теж varint
}

// Розібрати тег: номер, тип, число з'їдених байтів; ok=false при помилці.
func TagDecode(buf []byte) (fieldNum uint32, wireType uint8, n int, ok bool) {
	tag, n, ok := VarintDecodeU32(buf)
	if !ok { // обірваний/зіпсований тег
		return 0, 0, 0, false
	}
	wireType = uint8(tag & 0x07) // три молодші біти — тип
	fieldNum = tag >> 3          // решта — номер поля
	return fieldNum, wireType, n, true
}
