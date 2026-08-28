void Mat::deallocate()
{
    if(u)
    {
        UMatData* u_ = u;
        u = NULL;
        (u_->currAllocator ? u_->currAllocator : allocator ?
         allocator : getDefaultAllocator())->unmap(u_);
    }
}

void MatAllocator::unmap(UMatData* u) const
{
    if(u->urefcount == 0 && u->refcount == 0)
    {
        deallocate(u);
    }
}
