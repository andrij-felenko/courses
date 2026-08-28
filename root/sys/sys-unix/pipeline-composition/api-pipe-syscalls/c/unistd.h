#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>

// Дублювання в найменший вільний дескриптор
int dup(int oldfd);

// Атомарне дублювання newfd = oldfd з безпечним закриттям старого newfd
int dup2(int oldfd, int newfd);

// Розширене дублювання з атомарним прапорцем O_CLOEXEC
int dup3(int oldfd, int newfd, int flags);
