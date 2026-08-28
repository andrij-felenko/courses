package lexer

import "unicode"

type Kind int

const (
	Num Kind = iota
	Ident
	Plus
	Minus
	Star
	LParen
	RParen
	End
)

type Token struct {
	Kind  Kind
	Value int    // для Num — розібране число
	Text  string // для Ident — саме ім'я (лексема)
}

type Lexer struct {
	src []rune
	pos int // поточна позиція у вхідному тексті
}

func New(src string) *Lexer { return &Lexer{src: []rune(src)} }

func (l *Lexer) peek() rune {
	if l.pos < len(l.src) {
		return l.src[l.pos]
	}
	return 0
}

func (l *Lexer) Next() Token {
	for unicode.IsSpace(l.peek()) { // 1) проковтнути пробіли
		l.pos++
	}

	if l.peek() == 0 { // кінець вводу
		return Token{Kind: End}
	}

	if unicode.IsDigit(l.peek()) { // 2) НАЙДОВШЕ число
		v := 0
		for unicode.IsDigit(l.peek()) { // тягнемо цифри, доки йдуть
			v = v*10 + int(l.src[l.pos]-'0') // тут-таки рахуємо значення
			l.pos++
		}
		return Token{Kind: Num, Value: v}
	}

	if unicode.IsLetter(l.peek()) { // 3) НАЙДОВШЕ ім'я
		start := l.pos
		for unicode.IsLetter(l.peek()) || unicode.IsDigit(l.peek()) {
			l.pos++ // тягнемо буквоцифри
		}
		return Token{Kind: Ident, Text: string(l.src[start:l.pos])} // (ключові — нижче)
	}

	ch := l.src[l.pos] // 4) односимвольні оператори й дужки
	l.pos++
	switch ch {
	case '+':
		return Token{Kind: Plus}
	case '-':
		return Token{Kind: Minus}
	case '*':
		return Token{Kind: Star}
	case '(':
		return Token{Kind: LParen}
	case ')':
		return Token{Kind: RParen}
	default:
		return Token{Kind: End} // невідомий символ — тут спрощено
	}
}
