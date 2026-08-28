int acpi_status_to_errno(acpi_status status)
{
    switch (status) {
    case AE_OK:
        return 0;
    case AE_NOT_FOUND:
        return -ENODEV;
    case AE_BAD_PARAMETER:
        return -EINVAL;
    case AE_NO_MEMORY:
        return -ENOMEM;
    case AE_TIME:
        return -ETIMEDOUT;
    default:
        return -EIO;
    }
}
