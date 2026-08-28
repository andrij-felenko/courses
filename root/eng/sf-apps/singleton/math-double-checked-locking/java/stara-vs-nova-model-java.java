class Foo {
    private volatile Helper helper = null;     // ← єдина, але вирішальна відмінність

    public Helper getHelper() {
        if (helper == null) {                  // читання volatile: acquire-бар'єр
            synchronized (this) {
                if (helper == null)
                    helper = new Helper();      // запис volatile: release-бар'єр
            }
        }
        return helper;
    }
}
