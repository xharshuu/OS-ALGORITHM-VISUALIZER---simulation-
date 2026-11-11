"""
Page Replacement Algorithms: FIFO, LRU, and Optimal (OPT).
"""

from typing import Any, Dict, List


def simulate_page_replacement(
    reference_string: List[Any],
    num_frames: int,
    algorithm: str = "fifo",
) -> Dict[str, Any]:
    """
    Simulate virtual memory page replacement.

    Supported algorithms:
      - fifo: First-In First-Out
      - lru: Least Recently Used
      - optimal: Belady's Optimal Page Replacement

    Returns:
      Step-by-step grid of frame states, hits/faults, and performance summary.
    """
    if num_frames <= 0:
        raise ValueError("Number of frames must be a positive integer (> 0).")
    if not reference_string:
        raise ValueError("Reference string cannot be empty.")

    pages = [str(p).strip() for p in reference_string if str(p).strip()]
    if not pages:
        raise ValueError("Reference string contains no valid page numbers.")

    frames: List[str] = []
    steps = []
    fault_count = 0
    hit_count = 0

    # Tracking structures for algorithms
    # FIFO: order of arrival queue
    fifo_queue: List[str] = []
    # LRU: last accessed timestamp
    last_access: Dict[str, int] = {}

    for step_idx, page in enumerate(pages):
        is_hit = page in frames
        replaced_page = None

        if is_hit:
            hit_count += 1
            last_access[page] = step_idx
        else:
            fault_count += 1
            if len(frames) < num_frames:
                # Frame capacity available
                frames.append(page)
                fifo_queue.append(page)
            else:
                # Page replacement needed
                if algorithm == "fifo":
                    victim = fifo_queue.pop(0)
                    replaced_page = victim
                    victim_idx = frames.index(victim)
                    frames[victim_idx] = page
                    fifo_queue.append(page)

                elif algorithm == "lru":
                    # Find page in frames with smallest last_access timestamp
                    victim = min(frames, key=lambda p: last_access.get(p, -1))
                    replaced_page = victim
                    victim_idx = frames.index(victim)
                    frames[victim_idx] = page

                elif algorithm == "optimal":
                    # Look ahead in remaining pages (step_idx + 1 onwards)
                    future_pages = pages[step_idx + 1 :]
                    victim = None
                    furthest_next_use = -1

                    for f_page in frames:
                        if f_page not in future_pages:
                            # Not used in future at all! Best candidate
                            victim = f_page
                            break
                        else:
                            next_use_idx = future_pages.index(f_page)
                            if next_use_idx > furthest_next_use:
                                furthest_next_use = next_use_idx
                                victim = f_page

                    if victim is None:
                        victim = frames[0]

                    replaced_page = victim
                    victim_idx = frames.index(victim)
                    frames[victim_idx] = page
                else:
                    raise ValueError(f"Unknown page replacement algorithm: '{algorithm}'")

            last_access[page] = step_idx

        # Snapshot frame slots padded to num_frames
        frame_snapshot = list(frames) + ["-"] * (num_frames - len(frames))

        steps.append(
            {
                "step": step_idx + 1,
                "page": page,
                "frames": frame_snapshot,
                "is_hit": is_hit,
                "is_fault": not is_hit,
                "replaced_page": replaced_page,
            }
        )

    total_requests = len(pages)
    hit_ratio = round((hit_count / total_requests) * 100.0, 2)
    fault_ratio = round((fault_count / total_requests) * 100.0, 2)

    return {
        "algorithm": algorithm,
        "num_frames": num_frames,
        "reference_string": pages,
        "steps": steps,
        "summary": {
            "total_requests": total_requests,
            "total_faults": fault_count,
            "total_hits": hit_count,
            "hit_ratio": hit_ratio,
            "fault_ratio": fault_ratio,
        },
    }


def compare_page_replacements(reference_string: List[Any], num_frames: int) -> Dict[str, Any]:
    """Compare FIFO, LRU, and Optimal algorithms on the same reference string."""
    res_fifo = simulate_page_replacement(reference_string, num_frames, "fifo")
    res_lru = simulate_page_replacement(reference_string, num_frames, "lru")
    res_opt = simulate_page_replacement(reference_string, num_frames, "optimal")

    return {
        "num_frames": num_frames,
        "reference_string": res_fifo["reference_string"],
        "algorithms": {
            "fifo": res_fifo,
            "lru": res_lru,
            "optimal": res_opt,
        },
    }
