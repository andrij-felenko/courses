package hlc

import (
	"errors"
	"sync"
)

const (
	maxOffsetMs = 500     // терпимий відрив чужого годинника вперед, мс
	cMax        = 1 << 16 // 16 бітів під лічильник
)

var errTooFarAhead = errors.New("hlc: чужий годинник неправдоподібно попереду")

// Clock — гібридний годинник одного вузла. Мітка = пара (l, c).
type Clock struct {
	mu   sync.Mutex
	l    int64        // фізична частина: настінний час, мс від епохи
	c    int64        // лічильник, росте лише коли l не зрушив
	phys func() int64 // джерело настінного часу
}

func New(phys func() int64) *Clock { return &Clock{phys: phys} }

// Now — локальна подія АБО відправлення (одне й те саме правило).
func (h *Clock) Now() (l, c int64) {
	h.mu.Lock()
	defer h.mu.Unlock()
	lPrev := h.l
	h.l = max64(lPrev, h.phys())
	if h.l == lPrev {
		h.c++ // фізичний не обігнав l — цокаємо лічильник
	} else {
		h.c = 0 // фізичний вирвався вперед — лічильник з нуля
	}
	h.guard()
	return h.l, h.c
}

// Update — отримання повідомлення з міткою (lm, cm).
func (h *Clock) Update(lm, cm int64) (l, c int64, err error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	pt := h.phys()
	if lm > pt+maxOffsetMs {
		return 0, 0, errTooFarAhead // не даємо чужому годиннику отруїти наш l
	}
	lPrev := h.l
	h.l = max64(lPrev, lm, pt)
	switch {
	case h.l == lPrev && h.l == lm:
		h.c = max64(h.c, cm) + 1
	case h.l == lPrev:
		h.c++
	case h.l == lm:
		h.c = cm + 1
	default: // h.l == pt — фізичний обігнав усіх
		h.c = 0
	}
	h.guard()
	return h.l, h.c, nil
}

func (h *Clock) guard() {
	if h.c >= cMax {
		panic("hlc: переповнення лічильника — фізичний час стоїть надто довго")
	}
}

// Less — чи мітка (l1,c1) строго раніша за (l2,c2).
func Less(l1, c1, l2, c2 int64) bool {
	return l1 < l2 || (l1 == l2 && c1 < c2)
}

func max64(xs ...int64) int64 {
	m := xs[0]
	for _, x := range xs[1:] {
		if x > m {
			m = x
		}
	}
	return m
}
