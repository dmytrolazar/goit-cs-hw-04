import os
import multiprocessing
from collections import defaultdict
from multiprocessing import Queue
from time import time


def search_keywords_in_file(filename, keywords):
    """Функція для пошуку ключових слів у конкретному файлі."""
    result = defaultdict(list)
    try:
        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()
            for word in keywords:
                if word.lower() in text.lower():  # Ігноруємо регістр при пошуку
                    result[word].append(filename)
    except Exception as e:
        print(f"Помилка при читанні файлу {filename}: {e}")
    return result


def process_task(files, keywords, queue):
    """Завдання для окремого процесу."""
    local_result = defaultdict(list)
    for file in files:
        result = search_keywords_in_file(file, keywords)
        for k, v in result.items():
            local_result[k].extend(v)
    queue.put(local_result)


def multiprocessing_search(files, keywords):
    """Запускає багатопроцесорний пошук по файлах."""
    processes = []
    queue = Queue()
    results = defaultdict(list)

    # Розділяємо файли на частини для процесів
    num_processes = min(4, len(files))  # Максимум 4 процеси
    chunk_size = len(files) // num_processes if num_processes > 0 else 1
    for i in range(num_processes):
        start = i * chunk_size
        end = len(files) if i == num_processes - 1 else (i + 1) * chunk_size
        process = multiprocessing.Process(
            target=process_task, args=(files[start:end], keywords, queue)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    # Збираємо результати з черги
    while not queue.empty():
        result = queue.get()
        for k, v in result.items():
            results[k].extend(v)

    return results


# Виконання багатопроцесорного пошуку
if __name__ == "__main__":
    keywords = ["family", "accident", "people"]

    # Отримуємо список файлів та сортуємо їх за номерами
    files = [f for f in os.listdir(".") if f.endswith(".txt")]
    files.sort(key=lambda x: int(x[4]))

    print(f"Знайдені такі файли: {files}")  # Виведемо знайдені файли для перевірки

    if not files:
        print(f"Немає доступних текстових файлів для пошуку.")
    else:
        start_time = time()
        results_multiprocessing = multiprocessing_search(files, keywords)
        print(f"Багатопроцесорний пошук завершено за {time() - start_time:.4f} секунд.")

        print(f"Результати пошуку:")

        # Сортуємо файли в результатах перед виведенням
        sorted_results = defaultdict(list)
        for keyword in keywords:
            found_files = sorted(
                results_multiprocessing.get(keyword, []),
                key=lambda x: int(x[4]),
            )
            sorted_results[keyword] = found_files

        if sorted_results:
            for keyword in keywords:  # Виводимо результати в порядку ключових слів
                found_files = sorted_results[keyword]
                print(f"Ключове слово '{keyword}' знайдено у файлах: {found_files}")
        else:
            print(f"Жодних ключових слів не знайдено.")