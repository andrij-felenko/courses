$ readelf -s --dyn-syms -W sensor-agent

Symbol table '.dynsym' contains 18 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
     1: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND socket@GLIBC_2.2.5
     2: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND connect@GLIBC_2.2.5
     3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND sendto@GLIBC_2.2.5
     4: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND EVP_EncryptInit_ex@OPENSSL_3.0.0
     5: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND ptrace@GLIBC_2.2.5
     6: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND unlink@GLIBC_2.2.5
