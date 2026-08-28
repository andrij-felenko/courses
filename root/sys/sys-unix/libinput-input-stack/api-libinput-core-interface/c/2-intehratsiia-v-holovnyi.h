/* Отримання дескриптора сповіщень для реєстрації в epoll/poll з прапорцем EPOLLIN */
int libinput_get_fd(struct libinput *libinput);

/* Зчитування накопичених сирих даних ядра та переведення внутрішніх автоматів станів */
int libinput_dispatch(struct libinput *libinput);

/* Витягування наступної високорівневої події з внутрішньої черги (повертає NULL, якщо черга порожня) */
struct libinput_event *libinput_get_event(struct libinput *libinput);

/* Звільнення пам'яті обробленої події */
void libinput_event_destroy(struct libinput_event *event);
