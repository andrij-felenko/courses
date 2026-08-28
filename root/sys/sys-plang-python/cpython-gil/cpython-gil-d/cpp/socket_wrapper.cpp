// socket_wrapper.cpp
#include <Python.h>
#include <sys/socket.h>
#include <span>
#include <cstddef>

ssize_t custom_socket_receive_cpp(int socket_fd, std::span<char> buffer) noexcept {
    ssize_t bytes_read = 0;
    
    Py_BEGIN_ALLOW_THREADS
    bytes_read = recv(socket_fd, buffer.data(), buffer.size(), 0);
    Py_END_ALLOW_THREADS
    
    return bytes_read;
}
