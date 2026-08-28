#include <stddef.h>
#include <stdint.h>

/* Інтерфейс 1: Малювання */
typedef struct IDrawableVTable {
    void (*draw)(void *self);
} IDrawableVTable;

typedef struct IDrawable {
    const IDrawableVTable *vptr;
} IDrawable;

/* Інтерфейс 2: Серіалізація */
typedef struct ISerializableVTable {
    void (*serialize)(void *self, uint8_t *buffer, size_t max_len);
} ISerializableVTable;

typedef struct ISerializable {
    const ISerializableVTable *vptr;
} ISerializable;

/* Похідний клас Button реалізує обидва інтерфейси */
typedef struct Button {
    IDrawable drawable_base;         /* зміщення 0 */
    ISerializable serializable_base; /* зміщення sizeof(IDrawable) = 8 байтів */
    int width;
    int height;
} Button;

/* Цільові методи Button, що очікують покажчик саме на Button* */
static void button_real_draw(Button *b) {
    (void)b;
}

static void button_real_serialize(Button *b, uint8_t *buf, size_t len) {
    (void)b; (void)buf; (void)len;
}

/* Thunk для IDrawable (зміщення 0, коригування не потрібне) */
static void thunk_drawable_draw(void *self) {
    Button *b = (Button *)self;
    button_real_draw(b);
}

/* Thunk для ISerializable: self вказує на serializable_base!
   Потрібно скоригувати self назад на початок Button */
static void thunk_serializable_serialize(void *self, uint8_t *buf, size_t len) {
    uint8_t *ptr = (uint8_t *)self;
    /* Віднімаємо зміщення поля serializable_base відносно Button */
    Button *b = (Button *)(ptr - offsetof(Button, serializable_base));
    button_real_serialize(b, buf, len);
}

static const IDrawableVTable BUTTON_DRAWABLE_VTBL = {
    .draw = thunk_drawable_draw
};

static const ISerializableVTable BUTTON_SERIALIZABLE_VTBL = {
    .serialize = thunk_serializable_serialize
};

static void button_init(Button *b, int w, int h) {
    b->drawable_base.vptr = &BUTTON_DRAWABLE_VTBL;
    b->serializable_base.vptr = &BUTTON_SERIALIZABLE_VTBL;
    b->width = w;
    b->height = h;
}
