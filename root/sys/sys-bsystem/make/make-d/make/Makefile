# Варіант 1: об'єднання в один рядок оболонки через \
good_rule:
	cd src && gcc -c main.c

# Варіант 2: багаторядкова конструкція в одній оболонці
script_rule:
	for f in *.c; do \
		echo "Compiling $$f"; \
		gcc -c "$$f"; \
	done
