// Виділення та звільнення пам'яті у стилі C
struct Device {
    int id;
    char* buffer;
};

struct Device* dev = (struct Device*)malloc(sizeof(struct Device));
if (!dev) {
    return;
}
dev->id = 1;
dev->buffer = (char*)malloc(256); // Ручне конструювання полів

// Ручне очищення перед звільненням структури
free(dev->buffer);
free(dev);
