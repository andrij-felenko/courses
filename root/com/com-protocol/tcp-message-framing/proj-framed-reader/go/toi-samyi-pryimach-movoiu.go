const (
	hdrLen   = 4
	maxFrame = 1 << 20 // 1 МіБ — та сама стеля зі специфікації
)

var ErrFrameTooLarge = errors.New("кадр більший за стелю")

// ReadFrames читає кадри, доки потік не скінчиться.
// body чинний ЛИШЕ до повернення з onFrame — далі його перезапишуть.
func ReadFrames(r io.Reader, onFrame func(body []byte) error) error {
	br := bufio.NewReaderSize(r, 64<<10) // накопичувач живе тут
	var hdr [hdrLen]byte
	body := make([]byte, 0, 4096)

	for {
		if _, err := io.ReadFull(br, hdr[:]); err != nil {
			if err == io.EOF {
				return nil // потік скінчився РІВНО на межі кадру
			}
			return err // ErrUnexpectedEOF — обірвано посеред заголовка
		}

		n := binary.BigEndian.Uint32(hdr[:])
		if n > maxFrame { // стеля — ДО виділення пам'яті
			return ErrFrameTooLarge
		}

		if cap(body) < int(n) { // буфер тіла росте, але не всихає
			body = make([]byte, n)
		}
		body = body[:n]

		if _, err := io.ReadFull(br, body); err != nil {
			if err == io.EOF {
				err = io.ErrUnexpectedEOF // тіла не було зовсім — теж обрив
			}
			return err
		}

		if err := onFrame(body); err != nil {
			return err
		}
	}
}
