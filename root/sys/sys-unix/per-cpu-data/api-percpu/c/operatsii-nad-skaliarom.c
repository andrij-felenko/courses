this_cpu_read(pcp)                    /* → значення            */
this_cpu_write(pcp, val)
this_cpu_add(pcp, val)                this_cpu_sub(pcp, val)
this_cpu_inc(pcp)                     this_cpu_dec(pcp)
this_cpu_and(pcp, val)                this_cpu_or(pcp, val)
this_cpu_add_return(pcp, val)         this_cpu_sub_return(pcp, val)
this_cpu_inc_return(pcp)              this_cpu_dec_return(pcp)
this_cpu_xchg(pcp, nval)              /* → старе значення      */
this_cpu_cmpxchg(pcp, oval, nval)     /* → старе значення      */
this_cpu_try_cmpxchg(pcp, &oval, nval) /* → bool; свіжі ядра   */
