u64 i;
phys_addr_t start, end;

/* усе придатне, крім від'єднуваного та знайденого драйверами */
for_each_mem_range(i, &start, &end)
        pr_info("RAM %pa..%pa\n", &start, &end);

/* вільне = memory мінус reserved, з фільтром за вузлом і прапорцями */
for_each_free_mem_range(i, NUMA_NO_NODE, MEMBLOCK_NONE, &start, &end, NULL)
        pr_info("free %pa..%pa\n", &start, &end);
