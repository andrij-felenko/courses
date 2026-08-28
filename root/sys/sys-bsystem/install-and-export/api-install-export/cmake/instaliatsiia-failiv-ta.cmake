# Встановлення окремих файлів
install(FILES <file>...
        DESTINATION <dir>
        [PERMISSIONS <permissions>...]
        [CONFIGURATIONS <config>...]
        [COMPONENT <component>]
        [RENAME <new-name>]
        [OPTIONAL]
)

# Встановлення структури каталогів
install(DIRECTORY <dir>...
        DESTINATION <dir>
        [FILE_PERMISSIONS <permissions>...]
        [DIRECTORY_PERMISSIONS <permissions>...]
        [USE_SOURCE_PERMISSIONS]
        [CONFIGURATIONS <config>...]
        [COMPONENT <component>]
        [FILES_MATCHING]
        [PATTERN <pattern> | REGEX <regex>]
        [EXCLUDE] [PERMISSIONS <permissions>...]
)
