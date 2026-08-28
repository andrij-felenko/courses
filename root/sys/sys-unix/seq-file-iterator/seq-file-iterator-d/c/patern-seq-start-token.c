   static int my_seq_show(struct seq_file *m, void *v)
   {
       if (v == SEQ_START_TOKEN) {
           seq_puts(m, "ID     Name             Status     Temp(C)  BusErrors\n");
           seq_puts(m, "-----------------------------------------------------\n");
           return 0;
       }

       struct my_node *node = v;
       seq_printf(m, "%-6d %-16s %-10s %-8d %lu\n",
                  node->id, node->name, node->status, node->temp, node->errs);
       return 0;
   }
