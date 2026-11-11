"""
Memory Allocation Algorithms: First Fit, Best Fit, Worst Fit.
"""

from typing import Any, Dict, List


def allocate_memory(
    blocks_input: List[Dict[str, Any]],
    processes_input: List[Dict[str, Any]],
    algorithm: str = "first_fit",
) -> Dict[str, Any]:
    """
    Simulate contiguous memory partition allocation.

    Supported algorithms:
      - first_fit: Allocates the first block that is large enough.
      - best_fit: Allocates the smallest block that is large enough.
      - worst_fit: Allocates the largest block that is large enough.

    Inputs:
      blocks_input: [{'id': 'B1', 'size': 100}, ...]
      processes_input: [{'pid': 'P1', 'size': 50}, ...]

    Returns allocation table, updated blocks state, fragmentation metrics.
    """
    # Clone blocks to avoid mutating input
    blocks = [
        {
            "id": b.get("id", f"B{i+1}"),
            "initial_size": int(b["size"]),
            "remaining_size": int(b["size"]),
            "allocated_pid": None,
            "allocated_size": 0,
            "internal_frag": 0,
        }
        for i, b in enumerate(blocks_input)
    ]

    allocations = []
    total_memory = sum(b["initial_size"] for b in blocks)
    total_allocated_memory = 0
    total_internal_frag = 0

    for p in processes_input:
        pid = str(p.get("pid", "P")).strip()
        psize = int(p["size"])

        # Find eligible free blocks
        eligible_indices = [
            i
            for i, b in enumerate(blocks)
            if b["allocated_pid"] is None and b["remaining_size"] >= psize
        ]

        chosen_idx = None
        if eligible_indices:
            if algorithm == "first_fit":
                chosen_idx = eligible_indices[0]
            elif algorithm == "best_fit":
                # Minimum remaining_size that fits
                chosen_idx = min(
                    eligible_indices, key=lambda i: blocks[i]["remaining_size"]
                )
            elif algorithm == "worst_fit":
                # Maximum remaining_size
                chosen_idx = max(
                    eligible_indices, key=lambda i: blocks[i]["remaining_size"]
                )
            else:
                raise ValueError(f"Unknown memory allocation algorithm: '{algorithm}'")

        if chosen_idx is not None:
            blk = blocks[chosen_idx]
            internal_frag = blk["remaining_size"] - psize
            blk["allocated_pid"] = pid
            blk["allocated_size"] = psize
            blk["remaining_size"] = internal_frag
            blk["internal_frag"] = internal_frag

            total_allocated_memory += psize
            total_internal_frag += internal_frag

            allocations.append(
                {
                    "pid": pid,
                    "process_size": psize,
                    "allocated": True,
                    "block_id": blk["id"],
                    "block_initial_size": blk["initial_size"],
                    "internal_frag": internal_frag,
                }
            )
        else:
            allocations.append(
                {
                    "pid": pid,
                    "process_size": psize,
                    "allocated": False,
                    "block_id": None,
                    "block_initial_size": None,
                    "internal_frag": 0,
                }
            )

    unallocated_procs = [a for a in allocations if not a["allocated"]]
    free_blocks = [b for b in blocks if b["allocated_pid"] is None]
    total_free_memory = sum(b["remaining_size"] for b in free_blocks)

    # External fragmentation occurs if total free memory >= process size but no single block can fit it
    external_frag_warning = False
    for unp in unallocated_procs:
        if total_free_memory >= unp["process_size"]:
            external_frag_warning = True
            break

    return {
        "algorithm": algorithm,
        "allocations": allocations,
        "blocks": blocks,
        "summary": {
            "total_memory": total_memory,
            "allocated_memory": total_allocated_memory,
            "free_memory": total_free_memory,
            "total_internal_frag": total_internal_frag,
            "allocated_count": sum(1 for a in allocations if a["allocated"]),
            "unallocated_count": len(unallocated_procs),
            "external_fragmentation": external_frag_warning,
        },
    }
