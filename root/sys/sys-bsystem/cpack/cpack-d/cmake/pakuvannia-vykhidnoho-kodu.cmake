# Формати архівів сирців
set(CPACK_SOURCE_GENERATOR "TGZ;ZIP")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-src")

# Перелік регулярних виразів файлів для виключення
set(CPACK_SOURCE_IGNORE_FILES
    "/build/"
    "/\\\\.git/"
    "/\\\\.cache/"
    "/\\\\.vscode/"
    "/\\\\.idea/"
    "\\\\.o$"
    "\\\\.a$"
    "\\\\.so$"
    "\\\\.dylib$"
    "\\\\.dll$"
    "_CPack_Packages/"
    "CPack.*\\\\.cmake$"
)
