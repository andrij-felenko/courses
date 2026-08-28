class Foo {
    private Helper helper = null;

    public Helper getHelper() {
        if (helper == null) {                  // 1-ша перевірка — БЕЗ замка
            synchronized (this) {
                if (helper == null)            // 2-га перевірка — під замком
                    helper = new Helper();
            }
        }
        return helper;
    }
}
