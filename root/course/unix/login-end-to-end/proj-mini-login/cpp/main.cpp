#define _GNU_SOURCE
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <security/pam_appl.h>

extern char **environ;

// RAII обгортка для тимчасового вимкнення відлуння в терміналі
class TerminalEchoGuard {
public:
    TerminalEchoGuard() {
        tcgetattr(STDIN_FILENO, &old_termios_);
        termios new_termios = old_termios_;
        new_termios.c_lflag &= ~(ECHO | ECHOE | ECHOK | ECHONL);
        tcsetattr(STDIN_FILENO, TCSANOW, &new_termios);
    }

    ~TerminalEchoGuard() {
        tcsetattr(STDIN_FILENO, TCSANOW, &old_termios_);
    }

    TerminalEchoGuard(const TerminalEchoGuard&) = delete;
    TerminalEchoGuard& operator=(const TerminalEchoGuard&) = delete;

private:
    termios old_termios_{};
};

// RAII делегатор для автоматичного закриття дескриптора PAM
struct PamDeleter {
    void operator()(pam_handle_t *pamh) const noexcept {
        if (pamh) {
            pam_end(pamh, PAM_SUCCESS);
        }
    }
};

using PamHandlePtr = std::unique_ptr<pam_handle_t, PamDeleter>;

// Функція діалогу PAM мовою C++
static int login_conv_cpp(int num_msg, const struct pam_message **msg,
                          struct pam_response **resp, void * /*appdata_ptr*/) {
    if (num_msg <= 0 || num_msg > PAM_MAX_NUM_MSG) {
        return PAM_CONV_ERR;
    }

    auto *reply = static_cast<pam_response *>(std::calloc(num_msg, sizeof(pam_response)));
    if (!reply) {
        return PAM_BUF_ERR;
    }

    for (int i = 0; i < num_msg; ++i) {
        switch (msg[i]->msg_style) {
            case PAM_PROMPT_ECHO_OFF: {
                std::cout << msg[i]->msg << std::flush;
                std::string input;
                {
                    TerminalEchoGuard guard;
                    std::getline(std::cin, input);
                }
                std::cout << std::endl;
                reply[i].resp = strdup(input.c_str());
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_PROMPT_ECHO_ON: {
                std::cout << msg[i]->msg << std::flush;
                std::string input;
                std::getline(std::cin, input);
                reply[i].resp = strdup(input.c_str());
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_ERROR_MSG:
                std::cerr << msg[i]->msg << '\n';
                break;
            case PAM_TEXT_INFO:
                std::cout << msg[i]->msg << '\n';
                break;
            default:
                std::free(reply);
                return PAM_CONV_ERR;
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

int main(int argc, char *argv[]) {
    if (getuid() != 0) {
        std::cerr << "Помилка: програма вимагає прав root (UID 0)\n";
        return EXIT_FAILURE;
    }

    std::string username;
    if (argc > 1) {
        username = argv[1];
    } else {
        std::cout << "login: " << std::flush;
        if (!std::getline(std::cin, username) || username.empty()) {
            return EXIT_FAILURE;
        }
    }

    struct passwd *pw = getpwnam(username.c_str());
    if (!pw) {
        std::cerr << "Користувача не знайдено в базі passwd\n";
        return EXIT_FAILURE;
    }

    pam_conv conv = { login_conv_cpp, nullptr };
    pam_handle_t *raw_pamh = nullptr;

    int rc = pam_start("login", username.c_str(), &conv, &raw_pamh);
    if (rc != PAM_SUCCESS) {
        std::cerr << "Збій pam_start: " << pam_strerror(raw_pamh, rc) << '\n';
        return EXIT_FAILURE;
    }
    PamHandlePtr pamh(raw_pamh);

    rc = pam_authenticate(pamh.get(), 0);
    if (rc != PAM_SUCCESS) {
        std::cerr << "Помилка автентифікації: " << pam_strerror(pamh.get(), rc) << '\n';
        return EXIT_FAILURE;
    }

    rc = pam_acct_mgmt(pamh.get(), 0);
    if (rc != PAM_SUCCESS) {
        std::cerr << "Помилка валідації облікового запису: " << pam_strerror(pamh.get(), rc) << '\n';
        return EXIT_FAILURE;
    }

    if (pam_setcred(pamh.get(), PAM_ESTABLISH_CRED) != PAM_SUCCESS) {
        return EXIT_FAILURE;
    }

    if (pam_open_session(pamh.get(), 0) != PAM_SUCCESS) {
        std::cerr << "Збій відкриття сесії PAM\n";
        pam_setcred(pamh.get(), PAM_DELETE_CRED);
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        std::perror("fork");
        pam_close_session(pamh.get(), 0);
        pam_setcred(pamh.get(), PAM_DELETE_CRED);
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        // Дочірній процес: створення сесії та скидання прав
        setsid();

        if (initgroups(pw->pw_name, pw->pw_gid) < 0) {
            std::perror("initgroups");
            _exit(EXIT_FAILURE);
        }
        if (setgid(pw->pw_gid) < 0) {
            std::perror("setgid");
            _exit(EXIT_FAILURE);
        }
        if (setuid(pw->pw_uid) < 0) {
            std::perror("setuid");
            _exit(EXIT_FAILURE);
        }

        if (chdir(pw->pw_dir) < 0) {
            std::cerr << "Попередження: chdir $HOME зазнав невдачі, перехід у /\n";
            if (chdir("/") < 0) _exit(EXIT_FAILURE);
        }

        setenv("HOME", pw->pw_dir, 1);
        setenv("USER", pw->pw_name, 1);
        setenv("LOGNAME", pw->pw_name, 1);
        setenv("SHELL", pw->pw_shell, 1);

        char **pam_env = pam_getenvlist(pamh.get());
        if (pam_env) {
            for (char **e = pam_env; *e != nullptr; ++e) {
                putenv(*e);
            }
        }

        std::string shell_path = (pw->pw_shell && pw->pw_shell[0]) ? pw->pw_shell : "/bin/sh";
        std::string shell_name = shell_path.substr(shell_path.find_last_of('/') + 1);
        std::string argv0 = "-" + shell_name;

        std::vector<char *> args = { argv0.data(), nullptr };
        execve(shell_path.c_str(), args.data(), environ);

        std::perror("execve");
        _exit(EXIT_FAILURE);
    }

    int status = 0;
    waitpid(pid, &status, 0);

    pam_close_session(pamh.get(), 0);
    pam_setcred(pamh.get(), PAM_DELETE_CRED);

    return EXIT_SUCCESS;
}
