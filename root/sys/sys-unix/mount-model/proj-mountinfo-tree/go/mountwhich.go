// mountwhich.go — той самий алгоритм. Потрібен Go 1.21+ (пакет slices).
// go build -o mountwhich mountwhich.go
package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"slices"
	"strconv"
	"strings"
)

type Mount struct {
	ID, Parent  int
	Dev         string
	Root, Point string
	Opts        string
	Tags        []string // shared:12, master:7, unbindable…
	FsType      string
	Source      string
	SbOpts      string
	comps, rel  []string
	kids        []*Mount
}

func isOctal(c byte) bool { return c >= '0' && c <= '7' }

// Один прохід зліва направо. Послідовність замін тут була б помилкою:
// той порядок, що знімає \134 першим, псує імена зі справжнім слешем.
func unescape(s string) string {
	if !strings.Contains(s, `\`) {
		return s
	}
	var b strings.Builder
	b.Grow(len(s))
	for i := 0; i < len(s); {
		if s[i] == '\\' && i+3 < len(s) &&
			isOctal(s[i+1]) && isOctal(s[i+2]) && isOctal(s[i+3]) {
			v := int(s[i+1]-'0')<<6 | int(s[i+2]-'0')<<3 | int(s[i+3]-'0')
			if v <= 0xff {
				b.WriteByte(byte(v))
				i += 4
				continue
			}
		}
		b.WriteByte(s[i])
		i++
	}
	return b.String()
}

func splitPath(p string) []string {
	out := make([]string, 0, 8)
	for _, c := range strings.Split(p, "/") {
		if c != "" && c != "." {
			out = append(out, c)
		}
	}
	return out
}

// strings.Fields безпечний саме тому, що справжні пробільні всередині
// полів ядро вже екранувало — інакше різати рядок за пробілами не можна.
func parseLine(line string) (*Mount, error) {
	f := strings.Fields(line)
	sep := 6
	for sep < len(f) && f[sep] != "-" {
		sep++
	}
	if sep >= len(f) || len(f) < sep+4 {
		return nil, fmt.Errorf("немає роздільника «-» або замало полів")
	}
	id, err := strconv.Atoi(f[0])
	if err != nil {
		return nil, err
	}
	parent, err := strconv.Atoi(f[1])
	if err != nil {
		return nil, err
	}
	m := &Mount{
		ID: id, Parent: parent, Dev: f[2],
		Root:   unescape(f[3]),
		Point:  unescape(f[4]),
		Opts:   f[5],
		Tags:   slices.Clone(f[6:sep]),
		FsType: unescape(f[sep+1]),
		Source: unescape(f[sep+2]),
		SbOpts: strings.Join(f[sep+3:], " "),
	}
	m.comps = splitPath(m.Point)
	return m, nil
}

type Tree struct {
	byID    map[int]*Mount
	outside *Mount // вигаданий вузол: те, чого у файлі немає
}

func isPrefix(p, c []string) bool {
	return len(c) >= len(p) && slices.Equal(p, c[:len(p)])
}

func build(ms []*Mount) *Tree {
	t := &Tree{
		byID:    make(map[int]*Mount, len(ms)),
		outside: &Mount{ID: -1, Point: "?", Root: "/", FsType: "?", Source: "?"},
	}
	for _, m := range ms {
		t.byID[m.ID] = m
	}
	for _, m := range ms {
		p := t.byID[m.Parent]
		if p == m {
			p = nil // вершина дерева: батько — сам собі
		}
		if p != nil && !isPrefix(p.comps, m.comps) {
			fmt.Fprintf(os.Stderr, "монтування %d: точка %q не лежить під %q\n",
				m.ID, m.Point, p.Point)
			p = nil
		}
		if p == nil { // сирота: у chroot батьківський рядок не виводиться
			m.rel = m.comps
			t.outside.kids = append(t.outside.kids, m)
			continue
		}
		m.rel = m.comps[len(p.comps):]
		p.kids = append(p.kids, m)
	}
	return t
}

// Спуск крізь стос монтувань у цій самій позиції.
func descend(cur *Mount, pos []string) (*Mount, []string) {
	for {
		var next *Mount
		for _, k := range cur.kids {
			if slices.Equal(k.rel, pos) {
				next = k // збігів кілька — перемагає останній рядок
			}
		}
		if next == nil {
			return cur, pos
		}
		cur, pos = next, nil
	}
}

func (t *Tree) Resolve(path string) (*Mount, []string) {
	cur, pos := descend(t.outside, nil)
	for _, c := range splitPath(path) {
		pos = append(pos, c)
		cur, pos = descend(cur, pos)
	}
	return cur, pos
}

func inside(m *Mount, pos []string) string {
	base := strings.TrimSuffix(m.Root, "/")
	if len(pos) == 0 {
		if base == "" {
			return "/"
		}
		return base
	}
	return base + "/" + strings.Join(pos, "/")
}

func (t *Tree) dump(m *Mount, depth int) {
	note := ""
	if r, _ := t.Resolve(m.Point); r != m {
		note = fmt.Sprintf("   <- точка веде в %d", r.ID)
	}
	extra := ""
	if m.Root != "/" {
		extra = ", корінь " + m.Root
	}
	fmt.Printf("%*s[%d] %s  (%s, %s%s)%s\n", depth*2, "", m.ID, m.Point,
		m.FsType, m.Source, extra, note)
	for _, k := range m.kids {
		t.dump(k, depth+1)
	}
}

func slurp(path string) []byte {
	f, err := os.Open(path)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer f.Close()
	var data []byte
	buf := make([]byte, 1<<16)
	for {
		n, err := f.Read(buf)
		data = append(data, buf[:n]...)
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		if n == 0 {
			break
		}
	}
	return data
}

func main() {
	src := os.Getenv("MOUNTINFO")
	if src == "" {
		src = "/proc/self/mountinfo"
	}
	var ms []*Mount
	for _, line := range strings.Split(string(slurp(src)), "\n") {
		if strings.TrimSpace(line) == "" {
			continue
		}
		m, err := parseLine(line)
		if err != nil {
			fmt.Fprintf(os.Stderr, "не розібрано (%v): %s\n", err, line)
			continue
		}
		ms = append(ms, m)
	}
	t := build(ms)

	if len(os.Args) < 2 {
		for _, m := range t.outside.kids {
			t.dump(m, 0)
		}
		return
	}
	for _, arg := range os.Args[1:] {
		// Символьні посилання й ".." розкриваємо заздалегідь.
		q, err := filepath.Abs(arg)
		if err != nil {
			q = arg
		}
		if r, err := filepath.EvalSymlinks(q); err == nil {
			q = r
		}
		m, pos := t.Resolve(q)
		if m.ID < 0 {
			fmt.Printf("%s -> монтування у файлі відсутнє\n", q)
			continue
		}
		fmt.Printf("%s -> [%d] %s, %s %s, усередині ФС: %s\n",
			q, m.ID, m.Point, m.FsType, m.Source, inside(m, pos))
	}
}
