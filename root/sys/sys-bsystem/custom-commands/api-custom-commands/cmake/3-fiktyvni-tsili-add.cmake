add_custom_target(
    Name [ALL]
    [COMMAND command1 [ARGS] [args1...]]
    [COMMAND command2 [ARGS] [args2...]]
    [DEPENDS depend1 [depend2 ...]]
    [BYPRODUCTS [files...]]
    [WORKING_DIRECTORY dir]
    [COMMENT comment]
    [VERBATIM]
    [USES_TERMINAL]
    [COMMAND_EXPAND_LISTS]
    [SOURCES src1 [src2...]]
)
