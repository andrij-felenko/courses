void seq_printf(struct seq_file *m, const char *fmt, ...);
void seq_puts(struct seq_file *m, const char *s);
void seq_putc(struct seq_file *m, char c);
void seq_write(struct seq_file *m, const void *data, size_t len);
void seq_pad(struct seq_file *m, char c);
int  seq_escape(struct seq_file *m, const char *s, const char *esc);
void seq_hex_dump(struct seq_file *m, const char *prefix_str, int prefix_type,
                  int rowsize, int groupsize, const void *buf, size_t len,
                  bool ascii);
bool seq_has_overflowed(struct seq_file *m);
