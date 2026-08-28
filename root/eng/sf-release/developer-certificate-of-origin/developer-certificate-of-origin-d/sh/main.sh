# 2. Додаємо підпис до першого коміту, не змінюючи опис
git commit --amend -s --no-edit

# 3. Продовжуємо rebase до другого коміту
git rebase --continue

# 4. Виправляємо підпис у другому коміті, щоб він збігався з автором
git commit --amend -s --no-edit

# 5. Завершуємо rebase
git rebase --continue
