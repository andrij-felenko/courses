/* fs/namei.c, скорочено до суті */
int inode_permission(struct mnt_idmap *idmap, struct inode *inode, int mask)
{
    int retval;

    retval = sb_permission(inode->i_sb, inode, mask);   /* монтування лише для читання? */
    if (retval)
        return retval;

    retval = do_inode_permission(idmap, inode, mask);   /* дев'ять бітів, ACL, мандати */
    if (retval)
        return retval;

    retval = devcgroup_inode_permission(inode, mask);   /* обмеження на пристрої */
    if (retval)
        return retval;

    return security_inode_permission(inode, mask);      /* гачок LSM */
}
