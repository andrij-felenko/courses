// socket_wrapper.c
#include <Python.h>
#include <sys/socket.h>

ssize_t custom_socket_receive(int socket_fd, void *buffer, size_t size) {
    ssize_t bytes_read;
    
    Py_BEGIN_ALLOW_THREADS
    /* GIL вивільнено! Поточний потік не виконує байткод Python.
       Інтерпретатор вільний для виконання інших потоків. */
    bytes_read = recv(socket_fd, buffer, size, 0);
    Py_END_ALLOW_THREADS
    /* Після отримання даних потік знову захоплює GIL для створення об'єкта bytes */
    
    return bytes_read;
}
