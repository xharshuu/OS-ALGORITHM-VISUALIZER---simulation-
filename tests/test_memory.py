import pytest
from algorithms.memory import allocate_memory


def test_first_fit_allocation():
    blocks = [{"id": "B1", "size": 100}, {"id": "B2", "size": 500}, {"id": "B3", "size": 200}]
    processes = [{"pid": "P1", "size": 212}, {"pid": "P2", "size": 417}]

    # P1 (212) -> B2 (500)
    # P2 (417) -> None (no remaining free block >= 417)
    res = allocate_memory(blocks, processes, algorithm="first_fit")
    assert res["allocations"][0]["block_id"] == "B2"
    assert res["allocations"][0]["allocated"] is True
    assert res["allocations"][1]["allocated"] is False


def test_best_fit_allocation():
    blocks = [
        {"id": "B1", "size": 100},
        {"id": "B2", "size": 500},
        {"id": "B3", "size": 200},
        {"id": "B4", "size": 300},
        {"id": "B5", "size": 600},
    ]
    processes = [{"pid": "P1", "size": 212}]
    # Best fit should pick B4 (300), because 300 - 212 = 88 is the smallest leftover
    res = allocate_memory(blocks, processes, algorithm="best_fit")
    assert res["allocations"][0]["block_id"] == "B4"
    assert res["allocations"][0]["internal_frag"] == 88


def test_worst_fit_allocation():
    blocks = [
        {"id": "B1", "size": 100},
        {"id": "B2", "size": 500},
        {"id": "B3", "size": 200},
        {"id": "B4", "size": 300},
        {"id": "B5", "size": 600},
    ]
    processes = [{"pid": "P1", "size": 212}]
    # Worst fit picks B5 (600), leaving largest leftover = 388
    res = allocate_memory(blocks, processes, algorithm="worst_fit")
    assert res["allocations"][0]["block_id"] == "B5"
    assert res["allocations"][0]["internal_frag"] == 388
