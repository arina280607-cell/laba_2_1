import pytest
from src.contracts.task_source import TaskSource
from io import StringIO
from src.sources.stdin import StdinLineSource
from src.sources.json import JsonlSource
from src.sources.repository import REGISTRY
from src.inbox.core import InboxApp


class TestStdinSource:
    """Тесты для источника из stdin."""

    def test_fetch_single_task(self):
        """Тест чтения одной задачи."""
        stream = StringIO("task1:Hello world\n")
        source = StdinLineSource(stream=stream)

        tasks = list(source.fetch())
        assert len(tasks) == 1
        assert tasks[0].id == "task1"
        assert tasks[0].payload == "Hello world"  # strip() убирает \n

    def test_fetch_multiple_tasks(self):
        """Тест чтения нескольких задач."""
        stream = StringIO("task1:Hello\ntask2:World\n")
        source = StdinLineSource(stream=stream)

        tasks = list(source.fetch())
        assert len(tasks) == 2
        assert tasks[0].id == "task1"
        assert tasks[0].payload == "Hello"
        assert tasks[1].id == "task2"
        assert tasks[1].payload == "World"

    def test_skip_empty_lines(self):
        """Тест пропуска пустых строк."""
        stream = StringIO("task1:Hello\n\ntask2:World\n")
        source = StdinLineSource(stream=stream)

        tasks = list(source.fetch())
        # Из-за strip() пустая строка станет "" и будет пропущена
        assert len(tasks) == 2
        assert tasks[0].id == "task1"
        assert tasks[0].payload == "Hello"
        assert tasks[1].id == "task2"
        assert tasks[1].payload == "World"

    def test_task_without_payload(self):
        """Тест задачи без payload."""
        stream = StringIO("task1\n")
        source = StdinLineSource(stream=stream)

        tasks = list(source.fetch())
        assert len(tasks) == 1
        assert tasks[0].id == "task1"
        assert tasks[0].payload == ""

    def test_task_with_extra_spaces(self):
        """Тест задачи с пробелами."""
        stream = StringIO("  task1  :  Hello world  \n")
        source = StdinLineSource(stream=stream)

        tasks = list(source.fetch())
        assert len(tasks) == 1
        # strip() убирает пробелы по краям
        assert tasks[0].id == "task1"
        assert tasks[0].payload == "Hello world"


class TestJsonlSource:
    """Тесты для JSONL источника."""

    def test_fetch_from_jsonl(self, tmp_path):
        """Тест чтения из JSONL файла."""
        jsonl_file = tmp_path / "tasks.jsonl"
        jsonl_file.write_text(
            '{"id": "task1", "data": "hello"}\n'
            '{"id": "task2", "data": "world"}\n',
            encoding='utf-8'
        )

        source = JsonlSource(path=jsonl_file)
        tasks = list(source.fetch())

        assert len(tasks) == 2
        assert tasks[0].id == "task1"
        assert tasks[0].payload == {"data": "hello"}

    def test_auto_generate_id(self, tmp_path):
        """Тест автоматической генерации ID."""
        jsonl_file = tmp_path / "tasks.jsonl"
        jsonl_file.write_text('{"data": "test"}\n', encoding='utf-8')

        source = JsonlSource(path=jsonl_file)
        tasks = list(source.fetch())

        assert len(tasks) == 1
        assert tasks[0].id == "tasks.jsonl:1"
        assert tasks[0].payload == {"data": "test"}

    def test_invalid_json(self, tmp_path):
        """Тест обработки невалидного JSON."""
        jsonl_file = tmp_path / "tasks.jsonl"
        jsonl_file.write_text('{"id": "task1"}\ninvalid json\n', encoding='utf-8')

        source = JsonlSource(path=jsonl_file)

        with pytest.raises(ValueError, match="Bad JSON"):
            list(source.fetch())


class TestRepository:
    """Тесты для реестра источников."""

    def test_registry_contains_sources(self):
        """Тест наличия источников в реестре."""
        assert "stdin" in REGISTRY
        assert "file-jsonl" in REGISTRY

    def test_create_stdin_source(self):
        """Тест создания источника через фабрику."""
        source = REGISTRY["stdin"]()
        assert source.name == "stdin"
        assert hasattr(source, "fetch")

    def test_create_json_source(self, tmp_path):
        """Тест создания JSONL источника через фабрику."""
        source = REGISTRY["file-jsonl"](tmp_path / "test.jsonl")
        assert source.name == "file-jsonl"


class TestInboxApp:
    """Тесты для InboxApp."""

    def test_iter_messages(self):
        """Тест итерации по задачам из нескольких источников."""
        stream1 = StringIO("task1:Hello\n")
        stream2 = StringIO("task2:World\n")

        sources = [
            StdinLineSource(stream=stream1),
            StdinLineSource(stream=stream2),
        ]

        app = InboxApp(sources)
        tasks = list(app.iter_messages())

        assert len(tasks) == 2
        assert tasks[0].id == "task1"
        assert tasks[0].payload == "Hello"
        assert tasks[1].id == "task2"
        assert tasks[1].payload == "World"

    def test_empty_sources(self):
        """Тест с пустым списком источников."""
        app = InboxApp([])
        tasks = list(app.iter_messages())
        assert len(tasks) == 0

    def test_invalid_source(self):
        """Тест с некорректным источником."""
        app = InboxApp(["not a source"])
        with pytest.raises(TypeError, match="Source object must be TaskSource"):
            list(app.iter_messages())


class TestProtocol:
    """Тесты для проверки контрактов."""

    def test_isinstance_check(self):
        """Тест проверки через isinstance с Protocol."""
        source = StdinLineSource()
        assert isinstance(source, TaskSource)

    def test_hasattr_check(self):
        """Тест структурной проверки."""
        source = StdinLineSource()
        assert hasattr(source, 'name')
        assert hasattr(source, 'fetch')
        assert callable(source.fetch)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src"])