from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RfidRecord:
    epc: str
    timestamp: str
    rssi: int
    read_count: int
    line_number: int
    source_file: Path


def parse_rfid_line(line: str, line_number: int, source_file: Path) -> RfidRecord | None:
    parts = line.strip().split()
    if len(parts) < 5:
        return None

    try:
        rssi = int(parts[-2])
        read_count = int(parts[-1])
    except ValueError:
        return None

    return RfidRecord(
        epc=parts[0],
        timestamp=" ".join(parts[1:-2]),
        rssi=rssi,
        read_count=read_count,
        line_number=line_number,
        source_file=source_file,
    )


def read_log_file(path: Path, encoding: str = "utf-8") -> list[RfidRecord]:
    records = []
    with path.open("r", encoding=encoding, errors="replace") as log_file:
        for line_number, line in enumerate(log_file, start=1):
            record = parse_rfid_line(line, line_number, path)
            if record is not None:
                records.append(record)
    return records


def summarize_by_epc(
    records: list[RfidRecord], epcs: list[str]
) -> dict[str, dict[str, list[int] | int]]:
    epc_lookup = {epc.upper(): epc for epc in epcs}
    summary = {
        epc: {
            "rssi_values": [],
            "total_read_count": 0,
            "line_count": 0,
        }
        for epc in epcs
    }

    for record in records:
        selected_epc = epc_lookup.get(record.epc.upper())
        if selected_epc is None:
            continue

        summary[selected_epc]["rssi_values"].append(record.rssi)
        summary[selected_epc]["total_read_count"] += record.read_count
        summary[selected_epc]["line_count"] += 1

    return summary
