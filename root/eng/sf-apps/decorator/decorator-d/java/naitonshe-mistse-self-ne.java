interface Line {
    char at(int i);       // символ за індексом
    String render();      // увесь рядок
}

// КОНКРЕТНИЙ КОМПОНЕНТ: render() будує все ЧЕРЕЗ at()
class Plain implements Line {
    private final String s;
    Plain(String s) { this.s = s; }
    public char at(int i) { return s.charAt(i); }
    public String render() {
        var b = new StringBuilder();
        for (int i = 0; i < s.length(); i++)
            b.append(at(i));            // це this.at(i) — і в цьому вся сіль
        return b.toString();
    }
}

// БАЗОВИЙ ДЕКОРАТОР — делегує все
abstract class LineDecorator implements Line {
    protected final Line inner;
    protected LineDecorator(Line inner) { this.inner = inner; }
    public char at(int i)  { return inner.at(i); }
    public String render() { return inner.render(); }   // просто делегує
}

// КОНКРЕТНИЙ ДЕКОРАТОР: кожен символ — великим
class Upper extends LineDecorator {
    Upper(Line inner) { super(inner); }
    @Override public char at(int i) { return Character.toUpperCase(inner.at(i)); }
    // render() навмисно НЕ чіпаємо — хай делегується базовим декоратором
}

Line x = new Upper(new Plain("abc"));
x.at(0);       // 'A'   — decorate спрацював
x.render();    // "abc" — decorate ОБІЙДЕНО, малі літери!
