/* security/security.c */
int security_file_open(struct file *file)
{
	struct security_hook_list *hp;
	int rc;

	hlist_for_each_entry(hp, &security_hook_heads.file_open, list) {
		rc = hp->hook.file_open(file);
		if (rc)
			return rc; /* Short-circuit: відмова одного модуля зупиняє ланцюг */
	}
	return 0; /* Усі модулі в стеку дозволили операцію */
}
