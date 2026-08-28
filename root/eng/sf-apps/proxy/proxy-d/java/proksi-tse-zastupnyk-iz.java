interface Image {
    void draw();
    int width();
}

// Справжній об'єкт: створення = читання файлу з диска (дорого).
class RealImage implements Image {
    private final byte[] pixels;
    RealImage(String path) {
        this.pixels = loadFromDisk(path);   // читаємо ВЕСЬ файл уже в конструкторі
        System.out.println("завантажено " + path);
    }
    public void draw() { /* малюємо pixels */ }
    public int width() { return readWidthOf(pixels); }
}
