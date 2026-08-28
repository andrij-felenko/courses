// WriteFrame віддає кадр ОДНИМ записом: заголовок і тіло йдуть у стек
// разом, тіло нікуди не копіюється.
func WriteFrame(w io.Writer, body []byte) error {
	if len(body) > maxFrame {
		return ErrFrameTooLarge
	}
	var hdr [hdrLen]byte
	binary.BigEndian.PutUint32(hdr[:], uint32(len(body)))

	bufs := net.Buffers{hdr[:], body}
	_, err := bufs.WriteTo(w) // на TCP-з'єднанні — той самий розсіяний запис,
	return err                // а часткові записи WriteTo доганяє сама
}
