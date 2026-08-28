typedef int rl_command_func_t(int count, int key);

int rl_bind_key(int key, rl_command_func_t *function);
int rl_bind_keyseq(const char *seq, rl_command_func_t *function);
int rl_generic_bind(int type, const char *seq, char *data, Keymap map);
int rl_parse_and_bind(char *line);
int rl_read_init_file(const char *filename);
Keymap rl_get_keymap(void);
void rl_set_keymap(Keymap map);
Keymap rl_get_keymap_by_name(const char *name);
