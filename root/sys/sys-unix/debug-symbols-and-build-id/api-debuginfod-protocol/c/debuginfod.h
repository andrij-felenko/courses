#include <elfutils/debuginfod.h>

/* Створення дескриптора сесії клієнта */
debuginfod_client *debuginfod_begin(void);

/* Звільнення ресурсів сесії клієнта */
void debuginfod_end(debuginfod_client *client);

/* Прив'язка довільних контекстних даних користувача */
void debuginfod_set_user_data(debuginfod_client *client, void *data);
void *debuginfod_get_user_data(debuginfod_client *client);

/* Реєстрація функції зворотного виклику для відстеження прогресу */
typedef int (*debuginfod_progressfn_t)(debuginfod_client *client, long a, long b);
void debuginfod_set_progressfn(debuginfod_client *client, debuginfod_progressfn_t fn);

/* Пошук DWARF-файлу символів за Build ID */
int debuginfod_find_debuginfo(debuginfod_client *client,
                             const unsigned char *build_id,
                             int build_id_len,
                             char **path);

/* Пошук оригінального скомпільованого бінарника за Build ID */
int debuginfod_find_executable(debuginfod_client *client,
                              const unsigned char *build_id,
                              int build_id_len,
                              char **path);

/* Пошук сирцевого файлу за Build ID та шляхом */
int debuginfod_find_source(debuginfod_client *client,
                          const unsigned char *build_id,
                          int build_id_len,
                          const char *filename,
                          char **path);

/* Пошук окремої секції ELF за Build ID та назвою */
int debuginfod_find_section(debuginfod_client *client,
                           const unsigned char *build_id,
                           int build_id_len,
                           const char *section,
                           char **path);
