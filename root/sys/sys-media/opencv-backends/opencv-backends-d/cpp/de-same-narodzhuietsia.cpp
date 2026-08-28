Mat UMat::getMat(AccessFlag accessFlags) const
{
    if(!u)
        return Mat();
    accessFlags |= ACCESS_RW;
    UMatDataAutoLock autolock(u);
    ...
        if(CV_XADD(&u->refcount, 1) == 0)
            u->currAllocator->map(u, accessFlags);
        if (u->data != 0)
        {
            Mat hdr(dims, size.p, type(), u->data + offset, step.p);
            hdr.u = u;
            ...
            return hdr;
        }
    ...
}
