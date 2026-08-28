$ perf stat -e faults,minor-faults,major-faults,dTLB-loads,dTLB-load-misses ./my_app

 Performance counter stats for './my_app':

            12,450      faults
            12,448      minor-faults
                 2      major-faults
     1,420,551,102      dTLB-loads
           210,440      dTLB-load-misses          #    0.01% of all TLB accesses

       0.412891230 seconds time elapsed
