public final class Text {
    private final String value;
    private int hash;                 // навмисно НЕ final — лінивий кеш

    public Text(String v) { this.value = v; }

    @Override public int hashCode() {
        int h = hash;
        if (h == 0) {                 // ще не рахували
            h = value.hashCode();
            hash = h;                  // міняємо поле — але зовні нічого не змінилось
        }
        return h;
    }
}
