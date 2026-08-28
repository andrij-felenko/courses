pid_t pid = fork();
if (pid > 0) std::exit(0);

setsid();

pid = fork();
if (pid > 0) std::exit(0);

chdir("/");
umask(0);
for (int fd : {0, 1, 2}) close(fd);
int null_fd = open("/dev/null", O_RDWR);
dup2(null_fd, STDOUT_FILENO);
dup2(null_fd, STDERR_FILENO);

std::vector<char*> c_argv = { const_cast<char*>("/usr/sbin/daemon"), nullptr };
execve(c_argv[0], c_argv.data(), environ);
