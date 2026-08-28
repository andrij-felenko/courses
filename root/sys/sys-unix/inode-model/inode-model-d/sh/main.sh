$ stat -c '%i %h %n' notes.md
5107 1 notes.md          # номер inode, кількість імен, ім'я

$ ln notes.md draft.md   # новий запис у каталозі + 1 до лічильника
$ stat -c '%i %h %n' notes.md draft.md
5107 2 notes.md
5107 2 draft.md          # той самий об'єкт, два імені

$ mv draft.md ../draft.md   # у межах одного розділу: запис зник тут, з'явився там
$ stat -c '%h' notes.md
2                           # лічильник не змінився — імен так само два
