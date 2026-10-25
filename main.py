# Главный модуль: суммы диагоналей квадратной матрицы
from logger_module import setup_logger
import functions as fns

log = setup_logger()


def ask_matrix():
    # Меню с вопросом источника
    print("\nОткуда взять матрицу?")
    print("1 — ввести с клавиатуры")
    print("2 — прочитать из файла")
    choice = input("Выбор [1/2]: ").strip()
    try:
        if choice == "2":
            path = input("Путь к файлу: ").strip().strip('"').strip("'")
            m = fns.read_matrix_from_file(path)
            log.info("Матрица прочитана из '%s' (%dx%d)", path, len(m), len(m))
        else:
            n = int(input("Порядок матрицы n: ").strip())
            m = fns.matrix_input(n)
            log.info("Матрица введена с клавиатуры (%dx%d)", n, n)
    except (ValueError, FileNotFoundError, PermissionError) as e:
        print(f"Ошибка: {e}")
        log.error("Не удалось получить матрицу: %s", e)
        return None
    fns.matrix_print(m, "Ваша матрица:")
    log.debug("Матрица: %s", m)
    return m


def main():
    log.info("Программа запущена")
    m = ask_matrix()
    if m is None:
        log.info("Программа завершена без результата")
        return

    main_sum = fns.main_diagonal_sum(m)
    anti_sum = fns.anti_diagonal_sum(m)

    n = len(m)
    print(f"\nСумма главной диагонали (i == j):     {main_sum}")
    print(f"Сумма побочной диагонали (i + j == {n-1}): {anti_sum}")
    log.info("Главная диагональ = %s", main_sum)
    log.info("Побочная диагональ = %s", anti_sum)
    log.info("Программа завершена")


if __name__ == "__main__":
    main()