import "bytes"

// Безпечне порівняння імен MAVLink-параметрів (16 байтів, можливо без \0):
func nameEq(a, b []byte) bool {
    trim := func(s []byte) []byte {
        if len(s) > 16 {
            s = s[:16]
        }
        return bytes.TrimRight(s, "\x00")
    }
    return bytes.Equal(trim(a), trim(b))
}
