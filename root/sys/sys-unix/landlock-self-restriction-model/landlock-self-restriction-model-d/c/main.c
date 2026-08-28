static int add_path(int ruleset, const char *path, __u64 access)
{
	struct landlock_path_beneath_attr rule = { .allowed_access = access };
	int err;

	rule.parent_fd = open(path, O_PATH | O_CLOEXEC);
	if (rule.parent_fd < 0)
		return -1;
	err = syscall(__NR_landlock_add_rule, ruleset,
		      LANDLOCK_RULE_PATH_BENEATH, &rule, 0);
	close(rule.parent_fd);
	return err;
}
