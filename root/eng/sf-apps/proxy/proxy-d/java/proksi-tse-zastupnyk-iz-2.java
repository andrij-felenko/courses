class ImageProxy implements Image {
    private final String path;
    private RealImage real = null;      // ще немає — файл не читаний
    ImageProxy(String path) { this.path = path; }   // конструктор дешевий

    private RealImage load() {
        if (real == null) real = new RealImage(path);   // читаємо ОДИН раз
        return real;
    }
    public void draw() { load().draw(); }        // прийшли малювати → тепер треба справжній
    public int width() { return load().width(); }
}

// Клієнт не бачить різниці — тип той самий:
List<Image> gallery = paths.stream().map(ImageProxy::new).toList();
gallery.get(0).draw();   // читається РІВНО одна — перша
