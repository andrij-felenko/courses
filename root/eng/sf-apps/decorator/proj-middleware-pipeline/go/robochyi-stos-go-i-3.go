import "bytes"

// capture запам'ятовує статус і тіло, які глибші шари пишуть у відповідь,
// і водночас пропускає їх далі в справжній ResponseWriter.
type capture struct {
	http.ResponseWriter
	status int
	body   bytes.Buffer
}

func (c *capture) WriteHeader(code int) {
	c.status = code
	c.ResponseWriter.WriteHeader(code)
}

func (c *capture) Write(b []byte) (int, error) {
	c.body.Write(b)                 // запам'ятали копію тіла
	return c.ResponseWriter.Write(b) // і пропустили назовні
}
