void deallocate(UMatData* u) const CV_OVERRIDE
{
    if(!u) return;
    CV_Assert(u->urefcount == 0);
    CV_Assert(u->refcount == 0);
    if( !(u->flags & UMatData::USER_ALLOCATED) )
    {
        fastFree(u->origdata);
        u->origdata = 0;
    }
    delete u;
}
