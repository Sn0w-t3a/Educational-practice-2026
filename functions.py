# Суммы элементов главной и побочной диагоналей квадратной матрицы


def validate_square(m):
    # Проверяет, что m — непустая квадратная матрица (список списков)
    if not isinstance(m, list) or not m:
        raise ValueError("матрица пустая или не список")
    n = len(m)
    for i, row in enumerate(m):
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(f"не квадратная: строка {i} длины {len(row) if isinstance(row, list) else '?'}, ожидалось {n}")
    return n


def main_diagonal_sum(m):
    # Сумма элементов главной диагонали (i == j)
    n = validate_square(m)
    return sum(m[i][i] for i in range(n))


def anti_diagonal_sum(m):
    # Сумма элементов побочной диагонали (i + j == n - 1).
    n = validate_square(m)
    return sum(m[i][n - 1 - i] for i in range(n))


def matrix_input(n):
    # Ввод квадратной матрицы n×n с клавиатуры — по одному числу на строку
    if n <= 0:
        raise ValueError("Порядок матрицы должен быть > 0")
    matrix = []
    for i in range(n):
        print(f"Введите элементы {i + 1}-й строки (по одному числу на строку):")
        row = []
        for j in range(n):
            while True:
                s = input(f"  a[{i + 1}][{j + 1}] = ").strip().replace(",", ".")
                if not s:
                    print("  ! пустой ввод, повторите")
                    continue
                try:
                    try:
                        row.append(int(s))
                    except ValueError:
                        row.append(float(s))
                    break
                except ValueError:
                    print(f"  ! '{s}' не является числом")
        matrix.append(row)
    return matrix


def read_matrix_from_file(path):
    # Читает квадратную матрицу из текстового файла (числа через пробел/запятую)
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.replace(",", " ").split()
            if not parts:
                continue
            try:
                rows.append([int(p) if p.lstrip("-").isdigit() else float(p) for p in parts])
            except ValueError:
                raise ValueError(f"нечисловые данные в строке: '{line.strip()}'")
    if not rows:
        raise ValueError("файл пустой")
    validate_square(rows)   # бросит ValueError, если не квадратная
    return rows


def matrix_print(m, title=""):
    # Печатает матрицу
    if title:
        print(title)
    if not m:
        print("(пустая матрица)")
        return
    def fmt(x):
        return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)
    width = max(len(fmt(x)) for row in m for x in row)
    for row in m:
        print("  ".join(fmt(x).rjust(width) for x in row))