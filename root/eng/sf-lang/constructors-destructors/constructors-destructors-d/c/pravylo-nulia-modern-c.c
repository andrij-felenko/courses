#include <stdlib.h>
#include <string.h>

// У мові C аналог «Правила нуля» неможливий: будь-яка композиція структур
// вимагає написання повного ланцюжка ручних функцій init/destroy
typedef struct {
    char* username;
    int* permissions;
    size_t perm_count;
} UserProfileC;

void user_profile_destroy(UserProfileC* profile) {
    free(profile->username);
    free(profile->permissions);
    profile->username = NULL;
    profile->permissions = NULL;
    profile->perm_count = 0;
}
