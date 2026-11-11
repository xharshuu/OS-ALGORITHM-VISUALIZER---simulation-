import pytest
from algorithms.page_replacement import simulate_page_replacement, compare_page_replacements


def test_fifo_page_replacement():
    # Textbook reference string
    pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3]
    res = simulate_page_replacement(pages, num_frames=3, algorithm="fifo")
    assert res["summary"]["total_requests"] == 10
    assert res["summary"]["total_faults"] > 0
    assert res["summary"]["total_hits"] + res["summary"]["total_faults"] == 10


def test_lru_page_replacement():
    pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    res = simulate_page_replacement(pages, num_frames=3, algorithm="lru")
    assert res["algorithm"] == "lru"
    assert len(res["steps"]) == 12


def test_optimal_page_replacement():
    pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    res_opt = simulate_page_replacement(pages, num_frames=3, algorithm="optimal")
    res_fifo = simulate_page_replacement(pages, num_frames=3, algorithm="fifo")
    # Optimal should have <= page faults than FIFO
    assert res_opt["summary"]["total_faults"] <= res_fifo["summary"]["total_faults"]


def test_compare_page_replacements():
    pages = [7, 0, 1, 2, 0, 3]
    res = compare_page_replacements(pages, num_frames=3)
    assert "fifo" in res["algorithms"]
    assert "lru" in res["algorithms"]
    assert "optimal" in res["algorithms"]
