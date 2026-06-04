import importlib
from unittest.mock import MagicMock, patch

import ollama
import pytest

from mgallery.tag import (
    MAX_TAGS,
    TaggingError,
    check_ollama_available,
    extract_json,
    generate_tags,
    normalize_tags,
    run_tag,
)


def _chat_response(content: str | None) -> ollama.ChatResponse:
    return ollama.ChatResponse(message=ollama.Message(role="assistant", content=content))


def _list_response(model_names: list[str]) -> ollama.ListResponse:
    models = [
        ollama.ListResponse.Model(model=name, modified_at=None, digest=None, size=None, details=None)
        for name in model_names
    ]
    return ollama.ListResponse(models=models)


class TestNormalizeTags:
    def test_lowercase_and_trim(self):
        assert normalize_tags(["  SUNSET  ", "Beach"]) == ["sunset", "beach"]

    def test_removes_duplicates(self):
        assert normalize_tags(["sunset", "Sunset", "SUNSET", "beach"]) == ["sunset", "beach"]

    def test_drops_empty_strings(self):
        assert normalize_tags(["", "   ", "beach"]) == ["beach"]

    def test_skips_non_strings(self):
        assert normalize_tags(["beach", 123, None, "sea"]) == ["beach", "sea"]

    def test_caps_at_max_tags(self):
        tags = [f"tag{i}" for i in range(50)]
        result = normalize_tags(tags)
        assert len(result) == MAX_TAGS

    def test_empty_list(self):
        assert normalize_tags([]) == []


class TestExtractJson:
    def test_plain_json(self):
        assert extract_json('{"tags": ["a", "b"]}') == {"tags": ["a", "b"]}

    def test_markdown_fenced_json(self):
        assert extract_json('```json\n{"tags": ["a", "b"]}\n```') == {"tags": ["a", "b"]}

    def test_fenced_no_language(self):
        assert extract_json('```\n{"tags": ["a", "b"]}\n```') == {"tags": ["a", "b"]}

    def test_empty_response(self):
        with pytest.raises(TaggingError, match="empty"):
            extract_json("")

    def test_garbage_response(self):
        with pytest.raises(TaggingError, match="non-JSON"):
            extract_json("This is not JSON at all, just prose.")

    def test_fenced_invalid_json(self):
        with pytest.raises(TaggingError, match="invalid JSON"):
            extract_json("```json\n{not valid json}\n```")

    def test_top_level_array(self):
        with pytest.raises(TaggingError, match="not a JSON object"):
            extract_json('["a", "b"]')

    def test_top_level_null(self):
        with pytest.raises(TaggingError, match="not a JSON object"):
            extract_json("null")


class TestCheckOllamaAvailable:
    def test_passes_when_model_installed(self):
        client = MagicMock()
        client.list.return_value = _list_response(["gemma3:12b", "llama3:8b"])
        check_ollama_available(client, model="gemma3:12b", host="http://localhost:11434")

    def test_raises_when_model_missing(self):
        client = MagicMock()
        client.list.return_value = _list_response(["llama3:8b"])
        with pytest.raises(TaggingError, match="not available"):
            check_ollama_available(client, model="gemma3:12b", host="http://localhost:11434")

    def test_raises_when_no_models(self):
        client = MagicMock()
        client.list.return_value = _list_response([])
        with pytest.raises(TaggingError, match="not available"):
            check_ollama_available(client, model="gemma3:12b", host="http://localhost:11434")

    def test_connection_error_raises_tagging_error(self):
        client = MagicMock()
        client.list.side_effect = ConnectionError("connection refused")
        with pytest.raises(TaggingError, match="not running"):
            check_ollama_available(client, model="gemma3:12b", host="http://localhost:11434")

    def test_connection_error_uses_host_in_message(self):
        client = MagicMock()
        client.list.side_effect = ConnectionError("connection refused")
        with pytest.raises(TaggingError, match="http://custom-host:9999"):
            check_ollama_available(client, model="gemma3:12b", host="http://custom-host:9999")

    def test_response_error_raises_tagging_error(self):
        client = MagicMock()
        client.list.side_effect = ollama.ResponseError("server error", 500)
        with pytest.raises(TaggingError, match="Ollama request failed"):
            check_ollama_available(client, model="gemma3:12b", host="http://localhost:11434")

    def test_client_without_private_attribute_still_raises_tagging_error(self):
        client = MagicMock(spec=["list"])
        client.list.side_effect = ConnectionError("connection refused")
        with pytest.raises(TaggingError, match="not running"):
            check_ollama_available(client, model="gemma3:12b", host="http://localhost:11434")


class TestGenerateTags:
    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "nope.jpg"
        with pytest.raises(TaggingError, match="does not exist"):
            generate_tags(image_path=str(missing))

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_valid_response_returns_tags(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_client = MagicMock()
        mock_client.list.return_value = _list_response(["gemma3:12b"])
        mock_client.chat.return_value = _chat_response('{"tags": ["Sunset", "Beach", "Sea", "Sky", "Horizon"]}')
        mock_client_cls.return_value = mock_client

        result = generate_tags(image_path=str(image), model="gemma3:12b", host="http://localhost:11434")

        assert result == ["sunset", "beach", "sea", "sky", "horizon"]
        mock_check.assert_called_once()
        call_kwargs = mock_client.chat.call_args.kwargs
        assert call_kwargs["model"] == "gemma3:12b"
        assert call_kwargs["format"] == "json"
        assert call_kwargs["options"]["temperature"] == 0.2
        assert call_kwargs["messages"][0]["images"] == [str(image)]

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_markdown_fenced_response(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_client = MagicMock()
        mock_client.list.return_value = _list_response(["gemma3:12b"])
        mock_client.chat.return_value = _chat_response(
            '```json\n{"tags": ["Forest", "Mist", "Mood", "Green", "Trees"]}\n```'
        )
        mock_client_cls.return_value = mock_client

        result = generate_tags(image_path=str(image))

        assert result == ["forest", "mist", "mood", "green", "trees"]

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_connection_error_raises(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_check.side_effect = None
        mock_client = MagicMock()
        mock_client.chat.side_effect = ConnectionError("connection refused")
        mock_client_cls.return_value = mock_client

        with pytest.raises(TaggingError, match="not running"):
            generate_tags(image_path=str(image))

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_response_error_raises(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_check.side_effect = None
        mock_client = MagicMock()
        mock_client.chat.side_effect = ollama.ResponseError("model not found", 404)
        mock_client_cls.return_value = mock_client

        with pytest.raises(TaggingError, match="Ollama request failed"):
            generate_tags(image_path=str(image))

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_invalid_json_raises(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_client = MagicMock()
        mock_client.chat.return_value = _chat_response("Sorry, I cannot help with that.")
        mock_client_cls.return_value = mock_client

        with pytest.raises(TaggingError, match="non-JSON"):
            generate_tags(image_path=str(image))

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_none_content_raises(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_client = MagicMock()
        mock_client.chat.return_value = _chat_response(None)
        mock_client_cls.return_value = mock_client

        with pytest.raises(TaggingError, match="empty"):
            generate_tags(image_path=str(image))

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_missing_tags_key_raises(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_client = MagicMock()
        mock_client.chat.return_value = _chat_response('{"labels": ["x"]}')
        mock_client_cls.return_value = mock_client

        with pytest.raises(TaggingError, match="tags"):
            generate_tags(image_path=str(image))

    @patch("mgallery.tag.check_ollama_available")
    @patch("mgallery.tag.ollama.Client")
    def test_tags_not_a_list_raises(self, mock_client_cls, mock_check, tmp_path):
        image = tmp_path / "photo.jpg"
        image.write_bytes(b"\xff\xd8\xff")
        mock_client = MagicMock()
        mock_client.chat.return_value = _chat_response('{"tags": "sunset"}')
        mock_client_cls.return_value = mock_client

        with pytest.raises(TaggingError, match="tags"):
            generate_tags(image_path=str(image))


class TestRunTag:
    @patch("mgallery.tag.generate_tags")
    def test_prints_json_on_success(self, mock_generate, capsys, tmp_path):
        mock_generate.return_value = ["sunset", "beach"]
        run_tag(image_path=str(tmp_path / "photo.jpg"))
        captured = capsys.readouterr()
        assert captured.out.strip() == '{"tags": ["sunset", "beach"]}'
        assert captured.err == ""

    @patch("mgallery.tag.generate_tags")
    def test_exits_with_error_message_on_tagging_error(self, mock_generate, capsys, tmp_path):
        mock_generate.side_effect = TaggingError("Model 'gemma3:12b' is not available")
        with pytest.raises(SystemExit) as exc_info:
            run_tag(image_path=str(tmp_path / "photo.jpg"))
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Model 'gemma3:12b' is not available" in captured.err
        assert captured.out == ""


class TestDefaultModelEnvVar:
    def test_default_model_respects_ollama_model_env(self, monkeypatch):
        from mgallery import tag

        monkeypatch.setenv("OLLAMA_MODEL", "custom-model:7b")
        reloaded = importlib.reload(tag)
        try:
            assert reloaded.DEFAULT_MODEL == "custom-model:7b"
        finally:
            monkeypatch.delenv("OLLAMA_MODEL")
            importlib.reload(reloaded)

    def test_default_host_respects_ollama_host_env(self, monkeypatch):
        from mgallery import tag

        monkeypatch.setenv("OLLAMA_HOST", "http://custom-host:9999")
        reloaded = importlib.reload(tag)
        try:
            assert reloaded.DEFAULT_HOST == "http://custom-host:9999"
        finally:
            monkeypatch.delenv("OLLAMA_HOST")
            importlib.reload(reloaded)
