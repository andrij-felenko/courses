package main

import (
	"container/heap"
	"fmt"
)

const K = 5 // скільки різних операцій вкидає клієнт

// SplitMix64: увесь стан — одне 64-бітове число; next() — чиста функція від нього.
type Rand struct{ state uint64 }

func NewRand(seed uint64) *Rand { return &Rand{state: seed} }

func (r *Rand) next() uint64 {
	r.state += 0x9E3779B97F4A7C15
	z := r.state
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	return z ^ (z >> 31)
}

func (r *Rand) intn(n uint64) uint64  { return r.next() % n } // рівномірно в [0, n)
func (r *Rand) chance(pct uint64) bool { return r.intn(100) < pct }
