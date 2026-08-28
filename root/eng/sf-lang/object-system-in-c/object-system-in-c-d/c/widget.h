/* widget.h — публічний інтерфейс: внутрішня розкладка прихована */
#ifndef WIDGET_H
#define WIDGET_H

typedef struct Widget Widget;

Widget* widget_new(int x, int y);
void widget_free(Widget *self);
void widget_set_position(Widget *self, int x, int y);
void widget_get_position(const Widget *self, int *x, int *y);

#endif
