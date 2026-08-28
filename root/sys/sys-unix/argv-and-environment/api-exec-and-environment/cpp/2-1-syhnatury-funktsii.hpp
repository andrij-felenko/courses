// C++ Інтерфейс середовища stdlib.h / cstdlib
#include <cstdlib>

extern "C" {
extern char **environ;

char *getenv(const char *name);
int setenv(const char *name, const char *value, int overwrite);
int unsetenv(const char *name);
int putenv(char *string);
int clearenv(void);
}
