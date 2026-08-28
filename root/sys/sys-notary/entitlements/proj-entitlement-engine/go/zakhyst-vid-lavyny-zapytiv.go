type Call struct {
	wg  sync.WaitGroup
	val *EffectiveSnapshot
	err error
}

type Group struct {
	mu sync.Mutex
	m  map[string]*Call
}

func (g *Group) Do(key string, fn func() (*EffectiveSnapshot, error)) (*EffectiveSnapshot, error) {
	g.mu.Lock()
	if g.m == nil {
		g.m = make(map[string]*Call)
	}
	if c, ok := g.m[key]; ok {
		g.mu.Unlock()
		c.wg.Wait()
		return c.val, c.err
	}
	c := new(Call)
	c.wg.Add(1)
	g.m[key] = c
	g.mu.Unlock()

	c.val, c.err = fn()
	c.wg.Done()

	g.mu.Lock()
	delete(g.m, key)
	g.mu.Unlock()

	return c.val, c.err
}
