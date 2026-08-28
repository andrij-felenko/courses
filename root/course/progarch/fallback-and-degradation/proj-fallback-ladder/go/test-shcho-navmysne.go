// Підроблена залежність із перемикачем: down=true → кидає, наче хаб замовк.
type fakeDevice struct {
    down    bool
    reading Reading
}

func (d *fakeDevice) Read(id string) (Reading, error) {
    if d.down {
        return Reading{}, &TimeoutError{Key: id} // ← навмисно «вимкнена» залежність
    }
    return d.reading, nil
}

type mapCache[T any] struct{ m map[string]entry[T] }

func newMapCache[T any]() *mapCache[T]           { return &mapCache[T]{m: map[string]entry[T]{}} }
func (c *mapCache[T]) Get(k string) (entry[T], bool) { e, ok := c.m[k]; return e, ok }
func (c *mapCache[T]) Put(k string, v T)         { c.m[k] = entry[T]{value: v, at: time.Now()} }
func (c *mapCache[T]) seed(k string, v T, at time.Time) { c.m[k] = entry[T]{value: v, at: at} }
