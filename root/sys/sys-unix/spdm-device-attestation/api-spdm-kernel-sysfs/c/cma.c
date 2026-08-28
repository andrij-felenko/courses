/* Приклад внутрішньої структури бінарного атрибута sysfs у drivers/pci/pcie/cma.c */
static ssize_t spdm_cert_read(struct file *filp, struct kobject *kobj,
                              struct bin_attribute *bin_attr,
                              char *buf, loff_t off, size_t count)
{
    struct pci_dev *pdev = to_pci_dev(kobj_to_dev(kobj));
    struct pci_spdm_state *spdm = pdev->spdm_state;

    if (!spdm || !spdm->cert_chain)
        return -ENODATA;

    if (off >= spdm->cert_chain_len)
        return 0;

    if (off + count > spdm->cert_chain_len)
        count = spdm->cert_chain_len - off;

    memcpy(buf, spdm->cert_chain + off, count);
    return count;
}
