# Отримаємо хеш поточного комміта
$ git rev-parse HEAD
4a8d9b1c2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b

# Отримаємо вказівник на дерево файлів (Merkle Tree Root) у комміті
$ git cat-file -p HEAD
tree 8f2b3a4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
author Author Name <author@example.com> 1723632000 +0300
committer Author Name <author@example.com> 1723632000 +0300

# Розгорнемо корінь дерева: він містить хеші піддерев і blobs
$ git cat-file -p 8f2b3a4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
100644 blob 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b    README.md
040000 tree 9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a    src
