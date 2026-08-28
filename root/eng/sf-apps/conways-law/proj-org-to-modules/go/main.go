// Оргсхема -> передбачений граф модулів за законом Конвея.
// Вхід: команди й канали спілкування. Вихід: шви (інтерфейси) та
// компоненти зв'язності (майбутні автономні частини системи).
package main

import (
	"fmt"
	"sort"
)

type pair struct{ a, b string }

// ВХІД: граф організації як дані.
// У базовому випадку "одна команда — один модуль" team == module.
var teams = []string{"ord", "pay", "shp", "rep", "anl"}

// Канал = пара команд, які РЕАЛЬНО регулярно узгоджують роботу.
var channels = []pair{
	{"ord", "pay"}, // замовлення ↔ оплата
	{"ord", "shp"}, // замовлення ↔ доставка
	{"rep", "anl"}, // звіти ↔ аналітика (окрема пара)
}

// Матриця суміжності як мапа сусідств. Симетрична: канал двобічний.
func adjacency(teams []string, chans []pair) map[string]map[string]bool {
	adj := make(map[string]map[string]bool, len(teams))
	for _, t := range teams {
		adj[t] = map[string]bool{}
	}
	for _, c := range chans {
		adj[c.a][c.b] = true
		adj[c.b][c.a] = true // «говорити» взаємне: той самий стик в обидва боки
	}
	return adj
}

// Передбачені інтерфейси = канали, нормалізовані як (менший, більший).
func seams(chans []pair) []pair {
	set := map[pair]bool{}
	for _, c := range chans {
		if c.a > c.b {
			c.a, c.b = c.b, c.a // (ord,pay) і (pay,ord) — одне ребро
		}
		set[c] = true
	}
	out := make([]pair, 0, len(set))
	for p := range set {
		out = append(out, p)
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].a != out[j].a {
			return out[i].a < out[j].a
		}
		return out[i].b < out[j].b
	})
	return out
}

// Компоненти зв'язності = майбутні автономні частини системи.
func components(teams []string, adj map[string]map[string]bool) [][]string {
	seen := map[string]bool{}
	var result [][]string
	for _, start := range teams {
		if seen[start] {
			continue
		}
		// обхід завширшки від непозначеного вузла
		var group []string
		queue := []string{start}
		seen[start] = true
		for len(queue) > 0 {
			node := queue[0]
			queue = queue[1:]
			group = append(group, node)
			for nb := range adj[node] {
				if !seen[nb] {
					seen[nb] = true
					queue = append(queue, nb)
				}
			}
		}
		sort.Strings(group)
		result = append(result, group)
	}
	return result
}

func main() {
	adj := adjacency(teams, channels)
	ss := seams(channels)
	cc := components(teams, adj)

	fmt.Printf("Передбачені шви (інтерфейси): %d\n", len(ss))
	for _, s := range ss {
		fmt.Printf("  %s <-> %s\n", s.a, s.b)
	}
	fmt.Printf("\nАвтономні частини (компоненти зв'язності): %d\n", len(cc))
	for i, group := range cc {
		fmt.Printf("  #%d: {%s}\n", i+1, join(group))
	}
}

func join(xs []string) string {
	out := ""
	for i, x := range xs {
		if i > 0 {
			out += ", "
		}
		out += x
	}
	return out
}
