/* include/linux/dax.h */
static inline bool daxdev_mapping_supported(const struct vm_area_desc *desc,
                                            const struct inode *inode,
                                            struct dax_device *dax_dev)
{
	if (!vma_desc_test(desc, VMA_SYNC_BIT))   /* MAP_SYNC не просили */
		return true;
	if (!IS_DAX(inode))                       /* файл не в стані S_DAX */
		return false;
	return dax_synchronous(dax_dev);          /* пристрій синхронний? */
}
