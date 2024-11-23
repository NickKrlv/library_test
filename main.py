import json
import logging
import os
from datetime import datetime
from typing import List, Optional


logging.basicConfig(
    filename="library.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def log_event(message: str) -> None:
    """Логирует событие и выводит его в консоль."""
    logging.info(message)
    print(colored(message, "green"))


def colored(text: str, color: str) -> str:
    """Возвращает цветной текст для вывода в консоль."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


class Book:
    """Класс для представления книги."""

    def __init__(
        self,
        book_id: int,
        title: str,
        author: str,
        year: int,
        status: str = "в наличии",
    ):
        self.id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.status = status

    def to_dict(self) -> dict:
        """Преобразует объект книги в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data: dict) -> "Book":
        """Создает объект книги из словаря."""
        return Book(
            book_id=data["id"],
            title=data["title"],
            author=data["author"],
            year=data["year"],
            status=data["status"],
        )


class Library:
    """Класс для управления библиотекой."""

    def __init__(self, data_file: str = "library.json"):
        self.data_file = data_file
        self.books: List[Book] = []
        self.load_books()

    def save_books(self) -> None:
        """Сохраняет книги в файл."""
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(
                [book.to_dict() for book in self.books],
                file,
                ensure_ascii=False,
                indent=4,
            )

    def load_books(self) -> None:
        """Загружает книги из файла."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as file:
                self.books = [
                    Book.from_dict(book_data) for book_data in json.load(file)
                ]

    def add_book(self, title: str, author: str, year: int) -> None:
        """Добавляет книгу в библиотеку."""
        new_id = max((book.id for book in self.books), default=0) + 1
        if any(book.id == new_id for book in self.books):
            raise ValueError(f"Книга с id {new_id} уже существует.")
        new_book = Book(book_id=new_id, title=title, author=author, year=year)
        self.books.append(new_book)
        self.save_books()
        log_event(f"Книга '{title}' добавлена с id {new_id}.")  # Логирование

    def delete_book(self, book_id: int) -> None:
        """Удаляет книгу по id."""
        book = self.find_book_by_id(book_id)
        if book:
            self.books.remove(book)
            self.save_books()
            log_event(f"Книга с id {book_id} удалена.")  # Логирование
        else:
            print(colored(f"Книга с id {book_id} не найдена.", "red"))
            log_event(
                f"Попытка удалить книгу с id {book_id}, но она не найдена."
            )  # Логирование ошибки

    def find_book_by_id(self, book_id: int) -> Optional[Book]:
        """Ищет книгу по id."""
        return next((book for book in self.books if book.id == book_id), None)

    def list_books(self) -> None:
        """Выводит список всех книг."""
        if not self.books:
            print(colored("Библиотека пуста.", "yellow"))
            return
        for book in self.books:
            print(
                colored(
                    f"ID: {book.id}, Название: {book.title}, Автор: {book.author}, Год: {book.year}, Статус: {book.status}",
                    "grey",
                )
            )

    def search_books(self, query: str, field: str) -> List[Book]:
        """Ищет книги по полю (title, author, year)."""
        return [
            book
            for book in self.books
            if query.lower() in str(getattr(book, field, "")).lower()
        ]

    def update_status(self, book_id: int) -> None:
        """Обновляет статус книги после подтверждения."""
        book = self.find_book_by_id(book_id)
        if book:
            print(colored(f"Текущий статус книги: '{book.status}'.", "yellow"))
            confirm = input("Поменять ли статус на другой? (да/нет): ").strip().lower()
            if confirm == "да":
                new_status = "выдана" if book.status == "в наличии" else "в наличии"
                book.status = new_status
                self.save_books()
                log_event(
                    f"Статус книги с id {book_id} изменен на '{new_status}'."
                )  # Логирование
            else:
                print(colored("Статус книги не изменен.", "yellow"))
                log_event(f"Статус книги с id {book_id} не был изменен.")  # Логирование
        else:
            print(colored(f"Книга с id {book_id} не найдена.", "red"))
            log_event(
                f"Попытка изменить статус книги с id {book_id}, но книга не найдена."
            )  # Логирование ошибки


def main() -> None:
    """Основная функция для работы с библиотекой."""
    library = Library()

    while True:
        print(colored("\n--- Меню ---", "blue"))
        print(colored("1. Добавить книгу", "green"))
        print(colored("2. Удалить книгу", "green"))
        print(colored("3. Искать книгу", "green"))
        print(colored("4. Показать все книги", "green"))
        print(colored("5. Изменить статус книги", "green"))
        print(colored("6. Выход", "red"))

        choice = input(colored("Выберите действие: ", "blue"))

        match choice:
            case "1":
                title = input("Введите название книги: ")
                author = input("Введите автора книги: ")
                try:
                    year = int(input("Введите год издания: "))
                    if not 0 < year < datetime.now().year:
                        print(
                            colored(
                                f"Год должен быть больше 0 и меньше {datetime.now().year + 1}!",
                                "red",
                            )
                        )
                        continue
                except ValueError:
                    print(colored("Год должен быть числом!", "red"))
                    continue
                library.add_book(title, author, year)

            case "2":
                try:
                    book_id = int(input("Введите id книги для удаления: "))
                    library.delete_book(book_id)
                except ValueError:
                    print(colored("Id книги должен быть числом!", "red"))

            case "3":
                print(colored("Искать по:", "blue"))
                print("1. Названию")
                print("2. Автору")
                print("3. Году издания")
                field_choice = input("Выберите поле для поиска (1/2/3): ")

                field_mapping = {"1": "title", "2": "author", "3": "year"}
                field = field_mapping.get(field_choice)

                if not field:
                    print(colored("Неверный выбор поля.", "red"))
                    continue

                query = input(f"Введите строку для поиска по {field}: ")
                results = library.search_books(query, field)
                if results:
                    for book in results:
                        print(
                            f"ID: {book.id}, Название: {book.title}, Автор: {book.author}, Год: {book.year}, Статус: {book.status}"
                        )
                else:
                    print(colored("Книги не найдены.", "yellow"))

            case "4":
                library.list_books()

            case "5":
                try:
                    book_id = int(input("Введите id книги: "))
                    library.update_status(book_id)
                except ValueError:
                    print(colored("Id книги должен быть числом!", "red"))

            case "6":
                print(colored("Выход из программы.", "yellow"))
                break

            case _:
                print(colored("Неверный выбор, попробуйте снова.", "red"))


if __name__ == "__main__":
    main()
