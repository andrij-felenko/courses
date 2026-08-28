Mat& Mat::operator=(const Mat& m)
{
    if( this != &m )
    {
        if( m.u )
            CV_XADD(&m.u->refcount, 1);
        release();
        flags = m.flags;
        // ... далі копіюються всі поля заголовка
    }
    return *this;
}
