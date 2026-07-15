"""Tests for Structured Error Handler."""

import pytest

from project import (
    AppError,
    ConfigError,
    ErrorRecord,
    NotFoundError,
    OperationResult,
    ValidationError,
    capture_error,
    safe_process,
    summarise_results,
    validate_field,
    validate_record,
    validate_schema
)


# --- Custom exceptions ---

def test_app_error_has_code() -> None:
    """AppError should carry a code and context."""
    err = AppError("something broke", code="BROKEN", context={"key": "val"})
    assert err.code == "BROKEN"
    assert err.context["key"] == "val"
    assert str(err) == "something broke"


def test_validation_error_has_field() -> None:
    """ValidationError should carry a field name."""
    err = ValidationError("bad email", field="email")
    assert err.field == "email"
    assert err.code == "VALIDATION_ERROR"


def test_not_found_error() -> None:
    """NotFoundError should format resource and identifier."""
    err = NotFoundError("User", "42")
    assert "User" in str(err)
    assert "42" in str(err)
    assert err.code == "NOT_FOUND"


# --- capture_error ---

def test_capture_app_error() -> None:
    """capture_error should extract structured info from AppError."""
    try:
        raise ValidationError("bad", field="name")
    except Exception as exc:
        record = capture_error(exc)
    assert record.code == "VALIDATION_ERROR"
    assert record.field == "name"


def test_capture_unexpected_error() -> None:
    """capture_error should handle non-AppError exceptions."""
    try:
        raise ValueError("oops")
    except Exception as exc:
        record = capture_error(exc)
    assert record.code == "UNEXPECTED"
    assert "oops" in record.message


# --- validate_field ---

def test_validate_required_missing() -> None:
    """Missing required field should produce REQUIRED error."""
    errors = validate_field("name", "", {"required": True})
    assert len(errors) == 1
    assert errors[0].code == "REQUIRED"


def test_validate_min_length() -> None:
    """Too-short value should produce TOO_SHORT error."""
    errors = validate_field("pw", "ab", {"min_length": 8})
    assert any(e.code == "TOO_SHORT" for e in errors)


def test_validate_pattern() -> None:
    """Pattern mismatch should produce INVALID_FORMAT error."""
    errors = validate_field("email", "notanemail", {"pattern": r"^.+@.+\..+$"})
    assert any(e.code == "INVALID_FORMAT" for e in errors)


def test_validate_passes() -> None:
    """Valid field should produce no errors."""
    errors = validate_field("name", "Alice", {"required": True, "min_length": 2})
    assert len(errors) == 0


# --- validate_record ---

def test_validate_record_success() -> None:
    """Valid record should return success."""
    record = {"name": "Alice", "email": "a@b.com"}
    schema = {"name": {"required": True}, "email": {"required": True}}
    result = validate_record(record, schema)
    assert result.success is True


def test_validate_record_failure() -> None:
    """Invalid record should collect errors."""
    record = {"name": "", "email": ""}
    schema = {"name": {"required": True}, "email": {"required": True}}
    result = validate_record(record, schema)
    assert result.success is False
    assert len(result.errors) == 2


# --- safe_process and summarise ---

def test_safe_process() -> None:
    """Batch processing should collect results without crashing."""
    records = [{"name": "Alice"}, {"name": ""}]
    schema = {"name": {"required": True}}
    results = safe_process(records, schema)
    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is False


def test_summarise_results() -> None:
    """Summary should count passed/failed and group error codes."""
    results = [
        OperationResult(success=True),
        OperationResult(success=False, errors=[
            ErrorRecord(code="REQUIRED", message="missing"),
            ErrorRecord(code="REQUIRED", message="also missing"),
        ]),
    ]
    summary = summarise_results(results)
    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["error_counts"]["REQUIRED"] == 2

def test_main_missing_file(monkeypatch, capsys):
    """없는 파일을 주면 traceback 없이 친절한 메시지를 출력해야 한다."""
    from project import main
    # sys.argv를 가짜로: [프로그램명, 파일, --schema, 스키마]
    monkeypatch.setattr("sys.argv", ["project.py", "data/nope.json", "--schema", "data/nope.json"])
    with pytest.raises(SystemExit):
        main()   # 예외 없이 정상 종료해야 함 (return으로 빠져나오니까)
    captured = capsys.readouterr()   # 캡처된 출력 꺼내기
    assert "not found" in captured.out   # 친절한 메시지가 찍혔나?

def test_validate_schema_bad_rule() -> None:
    bad_schema = {"name": {"required":True, "typo_rule": 5}}
    with pytest.raises(ConfigError):
        validate_schema(bad_schema)

def test_validate_schema_ok() -> None:
    good_schema = {"name": { "required":True, "min_length": 2 }}
    validate_schema(good_schema)