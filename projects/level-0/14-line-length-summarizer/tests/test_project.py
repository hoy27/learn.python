"""Tests for Line Length Summarizer."""

from project import categorise_lengths, compute_stats, measure_lines, build_histogram


def test_measure_lines() -> None:
    """Each line length should be counted correctly."""
    lines = ["hi", "hello", "a"]
    assert measure_lines(lines) == [2, 5, 1]


def test_compute_stats_normal() -> None:
    """Stats should be correct for a normal list of lengths."""
    stats = compute_stats([10, 20, 30])
    assert stats["min"] == 10
    assert stats["max"] == 30
    assert stats["average"] == 20.0
    assert stats["median"] == 20
    assert stats["total_lines"] == 3


def test_compute_stats_empty() -> None:
    """An empty list should not crash; all stats should be zero."""
    stats = compute_stats([])
    assert stats["min"] == 0
    assert stats["max"] == 0
    assert stats["total_lines"] == 0


def test_categorise_lengths() -> None:
    """Lines should be grouped into short, medium, and long."""
    lengths = [10, 50, 90, 5, 75]
    cats = categorise_lengths(lengths)
    assert cats["short"] == 2   # 10 and 5
    assert cats["medium"] == 2  # 50 and 75
    assert cats["long"] == 1    # 90

def test_histogram_caps_bar_width() -> None:
    result = build_histogram([10000])
    assert result.count("#") <= 50

def test_compute_stats_median() -> None:
    """중앙값: 홀수 개수는 가운데 값, 짝수 개수는 가운데 두 값의 평균."""
    assert compute_stats([10, 20, 30])["median"] == 20       # 홀수
    assert compute_stats([10, 20, 30, 40])["median"] == 25.0  # 짝수
