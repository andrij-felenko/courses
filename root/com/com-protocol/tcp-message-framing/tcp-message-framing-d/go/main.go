// buf — накопичувач з'єднання, have — скільки в ньому байтів
func (c *Conn) onReadable() error {
	n, err := c.conn.Read(c.buf[c.have:])
	c.have += n

	off := 0 // скільки з буфера вже розібрано
	for c.have-off >= hdrLen { // заголовок цілий?
		raw := binary.BigEndian.Uint32(c.buf[off:])
		if raw > maxFrame { // стеля — ДО будь-якої арифметики
			return errProtocol
		}
		length := int(raw)
		if c.have-off < hdrLen+length { // тіло ще не все — чекаємо далі
			break
		}
		c.handleFrame(c.buf[off+hdrLen : off+hdrLen+length])
		off += hdrLen + length
	}
	copy(c.buf, c.buf[off:c.have]) // хвіст — на початок буфера
	c.have -= off

	if err == io.EOF {
		if c.have == 0 {
			return nil // кінець рівно на межі кадру — чисте завершення
		}
		return errTruncated // обірвано посеред кадру
	}
	return err
}
