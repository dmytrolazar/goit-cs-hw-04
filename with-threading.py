import os
import threading
from collections import defaultdict
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


def threaded_search(files, keywords):
    """Запускає багатопотоковий пошук по файлах."""
    threads = []
    results = defaultdict(list)
    lock = threading.Lock()

    def search_task(files_subset):
        local_result = defaultdict(list)
        for file in files_subset:
            result = search_keywords_in_file(file, keywords)
            for k, v in result.items():
                local_result[k].extend(v)
        with lock:
            for k, v in local_result.items():
                results[k].extend(v)

    # Розділяємо файли на частини для потоків
    num_threads = min(4, len(files))  # Максимум 4 потоки
    chunk_size = len(files) // num_threads if num_threads > 0 else 1
    for i in range(num_threads):
        start = i * chunk_size
        end = len(files) if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=search_task, args=(files[start:end],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results


# Виконання багатопотокового пошуку
if __name__ == "__main__":
    keywords = ["family", "accident", "people"]

    # Отримуємо список файлів та сортуємо їх за номерами
    files = [f for f in os.listdir(".") if f.endswith(".txt")]
    files.sort(key=lambda x: int(x[4]))

    print(f"Знайдено такі файли: {files}")  # Виведемо знайдені файли для перевірки

    if not files:
        print(f"Немає доступних текстових файлів для пошуку.")
    else:
        start_time = time()
        results_threading = threaded_search(files, keywords)
        print(f"Багатопотоковий пошук завершено за {time() - start_time:.4f} секунд.")

        print(f"Результати пошуку:")

        # Сортуємо файли перед виведенням
        sorted_results = defaultdict(list)
        for keyword in keywords:
            found_files = sorted(
                results_threading.get(keyword, []),
                key=lambda x: int(x[4]),
            )
            sorted_results[keyword] = found_files

        if sorted_results:
            for keyword in keywords:  # Виводимо результати в порядку ключових слів
                found_files = sorted_results[keyword]
                print(f"Ключове слово '{keyword}' знайдено у файлах: {found_files}")
        else:
            print(f"Жодних ключових слів не знайдено.")