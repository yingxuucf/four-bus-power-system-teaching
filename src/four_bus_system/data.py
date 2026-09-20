"""统一读取课程参数，避免各讲重复固化常数。"""

from __future__ import annotations

from importlib import resources
import json
from typing import Any


def load_config() -> dict[str, Any]:
    path = resources.files("four_bus_system").joinpath("data", "four_bus_system.json")
    return json.loads(path.read_text(encoding="utf-8"))


CONFIG = load_config()


def bus_index(bus_id: str) -> int:
    ids = [item["id"] for item in CONFIG["buses"]]
    try:
        return ids.index(bus_id)
    except ValueError as exc:
        raise KeyError(f"未知母线 {bus_id!r}") from exc


def branch_record(branch_id: str) -> dict[str, Any]:
    for item in CONFIG["branches"]:
        if item["id"] == branch_id:
            return item
    raise KeyError(f"未知支路 {branch_id!r}")
