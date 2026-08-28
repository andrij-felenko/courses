// КОРЕКТНИЙ ІДІОМАТИЧНИЙ ПАТТЕРН У C:
size_t new_cap = buf->capacity + (buf->capacity >> 1); // Геометричний ріст x1.5
int *tmp = (int*)realloc(buf->data, new_cap * sizeof(int));
if (!tmp) {
    // Обробка критичної ситуації: buf->data все ще доступний і містить коректні дані
    fprintf(stderr, "Помилка: не вдалося розширити надлишковий буфер\n");
    return false;
}
buf->data = tmp;
buf->capacity = new_cap;
