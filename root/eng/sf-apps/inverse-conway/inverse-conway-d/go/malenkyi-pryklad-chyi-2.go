// Каталог володіє кешем і дає назовні лише контракт.
// billing НЕ бачить ні mu, ні map — лише ці два методи.
type CatalogCache struct {
	mu   sync.Mutex             // нутро закрите: маленька літера — поза пакетом невидимо
	data map[Key]Value
}

func (c *CatalogCache) Get(k Key) (Value, bool) { // весь замок — усередині
	c.mu.Lock()
	defer c.mu.Unlock()
	v, ok := c.data[k]
	return v, ok
}

func (c *CatalogCache) Put(k Key, v Value) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.data[k] = v
}
