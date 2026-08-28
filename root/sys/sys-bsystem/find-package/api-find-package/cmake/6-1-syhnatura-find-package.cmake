include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(<PackageName>
    (DEFAULT_MSG | "Користувацьке повідомлення про помилку")
    REQUIRED_VARS <var1> [<var2>...]
    [VERSION_VAR <version_var>]
    [HANDLE_VERSION_RANGE]
    [HANDLE_COMPONENTS]
    [CONFIG_MODE]
    [NAME_MISMATCHED]
    [REASON_FAILURE_MESSAGE <reason_var>])
