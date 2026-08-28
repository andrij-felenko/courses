git submodule [--quiet] [--cached]
git submodule add [-b <branch>] [-f|--force] [--name <name>] [--reference <repo>] [--depth <depth>] [--] <repository> [<path>]
git submodule init [--] [<path>...]
git submodule deinit [-f|--force] (--all|[--] <path>...)
git submodule update [--init] [--remote] [-N|--no-fetch] [--merge|--rebase] [--recursive] [--depth <depth>] [--] [<path>...]
git submodule set-branch (-b <branch>|-d|--default) [--] <path>
git submodule set-url [--] <path> <newurl>
git submodule sync [--recursive] [--] [<path>...]
git submodule status [--cached] [--recursive] [--] [<path>...]
git submodule foreach [--recursive] <command>
git submodule absorbgitdirs [--] [<path>...]
