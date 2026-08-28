typedef struct {
    int x;
    int y;
} Widget;

typedef struct {
    Widget base;          /* Зсув 0 байтів від початку Button */
    char *label;          /* Зсув після sizeof(Widget) */
    bool is_pressed;
} Button;
