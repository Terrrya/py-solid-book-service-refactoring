import json
import xml.etree.ElementTree as ETree
from abc import ABC, abstractmethod
from typing import Optional, NoReturn


class Book:
    def __init__(self, title: str, content: str) -> None:
        self.title = title
        self.content = content


class DisplayStrategy(ABC):
    @abstractmethod
    def display(self, book: Book) -> None:
        pass


class SerializationStrategy(ABC):
    @abstractmethod
    def serialize(self, book: Book) -> str:
        pass


class Console(DisplayStrategy):
    def display(self, book: Book) -> None:
        print(book.content)


class Reverse(DisplayStrategy):
    def display(self, book: Book) -> None:
        print(book.content[::-1])


class JSONSerializer(SerializationStrategy):
    def serialize(self, book: Book) -> str:
        return json.dumps({"title": book.title, "content": book.content})


class XMLSerializer(SerializationStrategy):
    def serialize(self, book: Book) -> str:
        root = ETree.Element("book")
        title = ETree.SubElement(root, "title")
        title.text = book.title
        content = ETree.SubElement(root, "content")
        content.text = book.content
        return ETree.tostring(root, encoding="unicode")


class Display:
    def __init__(self, strategy: DisplayStrategy) -> None:
        self.strategy = strategy

    def action(self, book: Book) -> None:
        self.strategy.display(book)


class PrintBook:
    def __init__(self, strategy: DisplayStrategy) -> None:
        self.strategy = strategy

    def action(self, book: Book) -> None:
        if isinstance(self.strategy, Console):
            print(f"Printing the book: {book.title}...")
        elif isinstance(self.strategy, Reverse):
            print(f"Printing the book in reverse: {book.title}...")
        self.strategy.display(book)


class Serializer:
    def __init__(self, strategy: SerializationStrategy) -> None:
        self.strategy = strategy

    def action(self, book: Book) -> str:
        return self.strategy.serialize(book)


class Command:
    def __init__(self) -> None:
        self.allowed_commands = {
            "display": "display",
            "print": "print",
            "serialize": "serialization",
        }
        self.display_strategies = {"console": Console(), "reverse": Reverse()}
        self.serialization_strategies = {
            "json": JSONSerializer(),
            "xml": XMLSerializer(),
        }

    def create_error_msg(self, action: str, method_type: str) -> str:
        return f"Unknown {self.allowed_commands[action]} type: {method_type}"

    def check_command(
        self, action: str, method_type: str
    ) -> Optional[NoReturn]:
        if action not in self.allowed_commands.keys():
            raise ValueError(f"Unknown command: {action}")

        if (
            action in ("display", "print")
            and method_type not in self.display_strategies.keys()
        ):
            raise ValueError(self.create_error_msg(action, method_type))

        elif (
            action == "serialize"
            and method_type not in self.serialization_strategies.keys()
        ):
            raise ValueError(self.create_error_msg(action, method_type))

    def execute(self, cmd: tuple[str, str], book: Book) -> Optional[str]:
        action, method_type = cmd
        self.check_command(action, method_type)

        if action == "display":
            Display(self.display_strategies[method_type]).action(book)

        elif action == "print":
            PrintBook(self.display_strategies[method_type]).action(book)

        elif action == "serialize":
            return Serializer(
                self.serialization_strategies[method_type]
            ).action(book)

        else:
            raise ValueError(f"Unknown command: {action}")


def main(book: Book, commands: list[tuple[str, str]]) -> None | str:
    command_handler = Command()
    for cmd in commands:
        if result := command_handler.execute(cmd, book):
            return result


if __name__ == "__main__":
    sample_book = Book("Sample Book", "This is some sample content.")
    print(main(sample_book, [("display", "reverse"), ("serialize", "xml")]))
