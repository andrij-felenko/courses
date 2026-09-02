#ifndef PTY_PACKET_H
#define PTY_PACKET_H

/* Запускає команду під псевдотерміналом і крутить цикл ведучого боку
   в пакетному режимі TIOCPKT. Повертає код виходу дитини або 1. */
int pty_run(char *const argv[]);

#endif /* PTY_PACKET_H */
