import (
    "encoding/binary"
    "errors"
)

// Розбір заголовка magic(2) ver(1) flags(1) len(2) rsv(2) time_us(8), старший байт першим.
func decHeader(b []byte) (ver uint8, length uint16, tUs uint64, err error) {
    if len(b) < 16 {
        return 0, 0, 0, errors.New("короткий заголовок")
    }
    if binary.BigEndian.Uint16(b[0:]) != 0xa75e {
        return 0, 0, 0, errors.New("не той magic")
    }
    ver = b[2]
    length = binary.BigEndian.Uint16(b[4:])
    tUs = binary.BigEndian.Uint64(b[8:])
    return ver, length, tUs, nil
}
