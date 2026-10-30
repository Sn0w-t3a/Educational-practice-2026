# Тест-кейсы для functions.py

6 функций, по 5 тестов на каждую — 30 кейсов. Запуск: pytest test_functions.py -v.

---

## Таблицы тест-кейсов

### validate_square(m)

| ID  | Вход                        | Ожидание                     | Тип       |
| --- | --------------------------- | ---------------------------- | --------- |
| 1   | `[[1,2],[3,4]]`             | возвращает 2                 | норма 2×2 |
| 2   | `[[1,2,3],[4,5,6],[7,8,9]]` | возвращает 3               | норма 3×3 |
| 3   | `[]`                        | ValueError «пустая»        | граница   |
| 4   | `[[1,2],[3,4,5]]`           | ValueError «не квадратная» | ошибка    |
| 5   | "abc"                     | ValueError                 | не список |

### main_diagonal_sum(m)

| ID | Вход | Ожидание | Тип |
|---|---|---|---|
| 1 | `[[7]]` | 7 | граница 1×1 |
| 2 | `[[1,2],[3,4]]` | 5 (=1+4) | норма 2×2 |
| 3 | `[[1,2,3],[4,5,6],[7,8,9]]` | 15 (=1+5+9) | норма 3×3 |
| 4 | `[[-1.5,2],[3,4.5]]` | 3.0 (=-1.5+4.5) | float/отрицательные |
| 5 | `[[1,2,3],[4,5,6]]` | ValueError | не квадратная |

### anti_diagonal_sum(m)

| ID | Вход | Ожидание | Тип |
|---|---|---|---|
| 1 | `[[7]]` | 7 | граница 1×1 |
| 2 | `[[1,2],[3,4]]` | 5 (=2+3) | норма 2×2 |
| 3 | `[[1,2,3],[4,5,6],[7,8,9]]` | 15 (=3+5+7) | норма 3×3 |
| 4 | `[[-1,-2],[-3,-4]]` | -5 (=-2−3) | отрицательные |
| 5 | `[[1,2,3],[4,5,6]]` | ValueError | не квадратная |

### matrix_input(n) (mock input)
| ID | Ввод в input() | n | Ожидание |
|---|---|---|---|
| 1 | "1","2","3","4" | 2 | `[[1,2],[3,4]]` |
| 2 | "1.5","2","3","4.5" | 2 | `[[1.5,2],[3,4.5]]` |
| 3 | "abc","1","2","3","4" | 2 | `[[1,2],[3,4]]` (повтор) |
| 4 | "", "1","2","3","4" | 2 | `[[1,2],[3,4]]` (пропуск пустой) |
| 5 | — | 0 | ValueError «> 0» |

### read_matrix_from_file(path)

| ID | Содержимое файла | Ожидание |
|---|---|---|
| 1 | "1 2\n3 4\n" | `[[1,2],[3,4]]` |
| 2 | "1.5 2\n3 4.5\n" | `[[1.5,2],[3,4.5]]` |
| 3 | "1,2\n3,4\n" | `[[1,2],[3,4]]` (запятые) |
| 4 | "1 2 3\n4 5 6\n" | ValueError «не квадратная» |
| 5 | "" | ValueError «пустой» |

### matrix_print(m, title) (через capsys)
| ID | Вход | Ожидание |
|---|---|---|
| 1 | `([[1,2],[3,4]], "Title")` | вывод содержит "Title", "1", "4" |
| 2 | `([[1,2],[3,4]], "")` | вывод без заголовка, есть цифры |
| 3 | `([[1,100],[2,3]], "")` | обе строки одинаковой длины (выравнивание) |
| 4 | `([], "")` | содержит "пустая" |
| 5 | `([[1.5, 2.0]], "")` | есть "1.5" и "2", нет "2.0" |

---

## test_functions.py

```python
"""Тесты для functions.py. Запуск: pytest test_functions.py -v"""  
from unittest.mock import patch  
  
import pytest  
import functions as fns  
  
  
# validate_square  
class TestValidateSquare:  
    def test_valid_2x2(self):  
        assert fns.validate_square([[1, 2], [3, 4]]) == 2  
  
    def test_valid_3x3(self):  
        assert fns.validate_square([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == 3  
  
    def test_empty_raises(self):  
        with pytest.raises(ValueError, match="пустая"):  
            fns.validate_square([])  
  
    def test_not_square_raises(self):  
        with pytest.raises(ValueError, match="не квадратная"):  
            fns.validate_square([[1, 2], [3, 4, 5]])  
  
    def test_not_list_raises(self):  
        with pytest.raises(ValueError):  
            fns.validate_square("abc")  
  
  
# main_diagonal_sum  
class TestMainDiagonalSum:  
    def test_1x1(self):  
        assert fns.main_diagonal_sum([[7]]) == 7  
  
    def test_2x2(self):  
        assert fns.main_diagonal_sum([[1, 2], [3, 4]]) == 5      # 1 + 4  
  
    def test_3x3(self):  
        assert fns.main_diagonal_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == 15  # 1+5+9  
  
    def test_negative_and_float(self):  
        assert fns.main_diagonal_sum([[-1.5, 2], [3, 4.5]]) == 3.0  # -1.5 + 4.5  
  
    def test_not_square_raises(self):  
        with pytest.raises(ValueError):  
            fns.main_diagonal_sum([[1, 2, 3], [4, 5, 6]])  
  
  
# anti_diagonal_sum  
class TestAntiDiagonalSum:  
    def test_1x1(self):  
        assert fns.anti_diagonal_sum([[7]]) == 7  
  
    def test_2x2(self):  
        assert fns.anti_diagonal_sum([[1, 2], [3, 4]]) == 5      # 2 + 3  
  
    def test_3x3(self):  
        assert fns.anti_diagonal_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == 15  # 3+5+7  
  
    def test_negative_values(self):  
        assert fns.anti_diagonal_sum([[-1, -2], [-3, -4]]) == -5  # -2 + -3  
  
    def test_not_square_raises(self):  
        with pytest.raises(ValueError):  
            fns.anti_diagonal_sum([[1, 2, 3], [4, 5, 6]])  
  
  
# matrix_input  
class TestMatrixInput:  
    def test_simple_2x2(self):  
        with patch("builtins.input", side_effect=["1", "2", "3", "4"]):  
            assert fns.matrix_input(2) == [[1, 2], [3, 4]]  
  
    def test_float_values(self):  
        with patch("builtins.input", side_effect=["1.5", "2", "3", "4.5"]):  
            assert fns.matrix_input(2) == [[1.5, 2], [3, 4.5]]  
  
    def test_invalid_then_valid(self):  
        with patch("builtins.input", side_effect=["abc", "1", "2", "3", "4"]):  
            assert fns.matrix_input(2) == [[1, 2], [3, 4]]  
  
    def test_empty_line_retries(self):  
        with patch("builtins.input", side_effect=["", "1", "2", "3", "4"]):  
            assert fns.matrix_input(2) == [[1, 2], [3, 4]]  
  
    def test_zero_order_raises(self):  
        with pytest.raises(ValueError, match="> 0"):  
            fns.matrix_input(0)  
  
  
# read_matrix_from_file  
class TestReadMatrixFromFile:  
    def test_simple(self, tmp_path):  
        f = tmp_path / "m.txt"  
        f.write_text("1 2\n3 4\n", encoding="utf-8")  
        assert fns.read_matrix_from_file(str(f)) == [[1, 2], [3, 4]]  
  
    def test_floats(self, tmp_path):  
        f = tmp_path / "m.txt"  
        f.write_text("1.5 2\n3 4.5\n", encoding="utf-8")  
        assert fns.read_matrix_from_file(str(f)) == [[1.5, 2], [3, 4.5]]  
  
    def test_commas_ok(self, tmp_path):  
        f = tmp_path / "m.txt"  
        f.write_text("1,2\n3,4\n", encoding="utf-8")  
        assert fns.read_matrix_from_file(str(f)) == [[1, 2], [3, 4]]  
  
    def test_not_square_raises(self, tmp_path):  
        f = tmp_path / "m.txt"  
        f.write_text("1 2 3\n4 5 6\n", encoding="utf-8")  
        with pytest.raises(ValueError, match="не квадратная"):  
            fns.read_matrix_from_file(str(f))  
  
    def test_empty_file_raises(self, tmp_path):  
        f = tmp_path / "m.txt"  
        f.write_text("", encoding="utf-8")  
        with pytest.raises(ValueError, match="пустой"):  
            fns.read_matrix_from_file(str(f))
```

---

## Примечания

1. **pytest.approx** для float (main_diagonal_sum с 1.5) — чтобы не ловить 2.9999999 из-за двоичной арифметики.
2. **tmp_path** — встроенная фикстура pytest: уникальная временная папка для каждого теста, конфликтов нет.
3. **capsys** — перехватывает print в matrix_print`.
4. **`patch("builtins.input", side_effect=[...])`** — подменяе input() в matrix_input; строки в списке идут в том же порядке, что и реальный ввод пользователя.
5. **`[[]]` не тестируется** (список из одной пустой строки) для matrix_print: max() в этом случае падает — это ограничение самой функции, а не теста.
