import "encoding/binary"

func encHeader(length uint16, tUs uint64) []byte {
    b := make([]byte, 16)
    binary.BigEndian.PutUint16(b[0:], 0xa75e) // magic
    b[2], b[3] = 2, 0                          // ver, flags
    binary.BigEndian.PutUint16(b[4:], length)
    binary.BigEndian.PutUint16(b[6:], 0)       // rsv
    binary.BigEndian.PutUint64(b[8:], tUs)
    return b
}
