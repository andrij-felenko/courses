// вбудовування io.Reader: усі його методи Go переспрямує сам
type CountingReader struct {
    io.Reader        // вбудований інтерфейс — не поле з іменем, а embedding
    n int64
}

func (c *CountingReader) Read(p []byte) (int, error) {
    k, err := c.Reader.Read(p)   // делегуємо вбудованому
    c.n += int64(k)              // додаємо своє — рахуємо байти
    return k, err
}
// якби в інтерфейсі були й інші методи, Go підвищив би їх до CountingReader
// автоматично — писати делегацію для них не треба
