#include <sys/types.h>
#include <sys/acl.h>          /* збирати з -lacl */

static int set_acl_text(const char *path, const char *spec)
{
    acl_t acl = acl_from_text(spec);
    if (!acl)                       /* EINVAL — рядок не розібрався */
        return -1;

    int rc = -1;
    if (acl_calc_mask(&acl) == 0    /* без цього наступний рядок відмовить */
        && acl_valid(acl) == 0      /* EINVAL — бракує базових записів */
        && acl_set_file(path, ACL_TYPE_ACCESS, acl) == 0)
        rc = 0;

    acl_free(acl);                  /* errno зберігається */
    return rc;
}

/* set_acl_text(path, "u::rw-,u:hanna:rw-,g::r--,o::---"); */
