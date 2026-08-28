#include <stdio.h>
#include <stdlib.h>

/* Оголошення таблиці класу (vtable) базового типу */
typedef struct Widget Widget;
typedef struct WidgetClass WidgetClass;

struct WidgetClass {
    void (*draw)(Widget *self);
    void (*handle_click)(Widget *self, int x, int y);
};

/* Базовий примірник */
struct Widget {
    const WidgetClass *klass; /* Вказівник на таблицю vtable (зсув 0) */
    int x, y;
};

void widget_draw_default(Widget *self) {
    printf("Base Widget drawing at (%d, %d)\n", self->x, self->y);
}

static const WidgetClass g_widget_class = {
    .draw = widget_draw_default,
    .handle_click = NULL
};

/* Нащадок: Button */
typedef struct Button Button;
typedef struct ButtonClass ButtonClass;

struct ButtonClass {
    WidgetClass parent_class; /* Вкладення таблиці предка (зсув 0) */
    void (*on_pressed)(Button *self);
};

struct Button {
    Widget base;              /* Вкладення екземпляра предка (зсув 0) */
    const char *label;
};

void button_draw_override(Widget *self) {
    Button *btn = (Button*)self;
    printf("Button drawing [%s] at (%d, %d)\n", btn->label, self->x, self->y);
}

static const ButtonClass g_button_class = {
    .parent_class = {
        .draw = button_draw_override,
        .handle_click = NULL
    },
    .on_pressed = NULL
};

/* Поліморфний виклик */
void render_scene(Widget *w) {
    /* Непрямий виклик через vtable: аналог w->draw() у C++ */
    if (w && w->klass && w->klass->draw) {
        w->klass->draw(w);
    }
}

int main(void) {
    Widget base_obj = { .klass = &g_widget_class, .x = 10, .y = 20 };
    Button btn_obj = { 
        .base = { .klass = (const WidgetClass*)&g_button_class, .x = 100, .y = 200 },
        .label = "Submit"
    };

    render_scene(&base_obj);
    render_scene((Widget*)&btn_obj); /* Двійковий поліморфізм у дії */
    return 0;
}
