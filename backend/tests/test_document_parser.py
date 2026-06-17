import anyio
import pytest

from app.services.document_parser import DocumentParserService, UnsupportedDocumentError


class FakeUpload:
    def __init__(self, filename: str, content: bytes) -> None:
        self.filename = filename
        self._content = content

    async def read(self) -> bytes:
        return self._content


def extract(filename: str, content: bytes) -> str:
    return anyio.run(DocumentParserService().extract_text, FakeUpload(filename, content))


def test_extracts_text_markdown_csv_and_json() -> None:
    assert extract("sample.txt", b"hello process") == "hello process"
    assert extract("sample.md", b"# Heading") == "# Heading"
    assert extract("sample.csv", b"name,value\nMaterial,123") == "name | value\nMaterial | 123"
    assert '"priority": "Must"' in extract("sample.json", b'{"priority":"Must"}')


def test_rejects_unsupported_document_type() -> None:
    with pytest.raises(UnsupportedDocumentError, match="Unsupported file type"):
        extract("sample.exe", b"not allowed")


def test_binary_extractors_raise_clear_errors_for_invalid_files() -> None:
    parser = DocumentParserService()

    with pytest.raises(UnsupportedDocumentError):
        parser._extract_pdf(b"%PDF")
    with pytest.raises(UnsupportedDocumentError):
        parser._extract_docx(b"docx")
    with pytest.raises(UnsupportedDocumentError):
        parser._extract_xlsx(b"xlsx")
