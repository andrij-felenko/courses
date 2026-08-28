# zpool status -D pool
  pool: pool
 state: ONLINE
  scan: scrub repaired 0B in 00:05:12 with 0 errors on Wed Aug 12 10:00:00 2026

DDT entries 524288, alloc 160M, metadata 32M, blocks 1048576

deduplicated blocks = 1048576, allocated count = 524288, ratio = 2.00x

DDT histogram (allocated blocks):

bucket              allocated             referenced          
------+------------------+------------------
refcnt              blocks   LSIZE   PSIZE      blocks   LSIZE   PSIZE
------              ------   -----   -----      ------   -----   -----
     2               524288   64G     32G       1048576  128G     64G
 Total               524288   64G     32G       1048576  128G     64G
