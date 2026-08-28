# збираємо дерево
root = Folder()
src = Folder()
src.add(File(1200))
src.add(File(800))
root.add(src)
root.add(File(500))

# а тепер — увага — клієнт НЕ знає й не питає, що перед ним
print(root.size())        # 2500
print(src.size())         # 2000
print(File(42).size())    # 42 — той самий виклик
