import argparse
import re
from pathlib import Path

from rfid_log_utils import read_log_file, summarize_by_epc
from rfid_plot_style import (
    ACADEMIC_COLORS,
    apply_academic_style,
    boxplot_style,
    make_tag_labels,
    print_tag_mapping,
    style_axis,
)


SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".pdf", ".py", ".pyc"}


def import_matplotlib():
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch
    except ImportError as exc:
        raise SystemExit(
            "matplotlib is required for plotting. Install it with: python3 -m pip install matplotlib"
        ) from exc
    apply_academic_style(plt)
    return plt, Patch


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot grouped RSSI boxes and read-count lines from multiple RFID log files."
    )
    parser.add_argument("--folder", required=True, help="Folder containing RFID log files.")
    parser.add_argument(
        "--epcs",
        nargs="+",
        required=True,
        help="Selected EPC values to compare, for example three tag IDs.",
    )
    parser.add_argument(
        "--pattern",
        default="*",
        help="Filename pattern to load inside the folder. Default: *",
    )
    parser.add_argument(
        "--output",
        help="Output image path. Default: <folder>/rfid_folder_summary.png",
    )
    parser.add_argument("--noshow", action="store_true", help="Not Display the plot window.")
    parser.add_argument("--title", help="Optional plot title.")
    return parser.parse_args()


def natural_sort_key(path):
    key = []
    for part in re.split(r"(\d+(?:\.\d+)?)", path.name):
        if not part:
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", part):
            key.append((1, float(part)))
        else:
            key.append((0, part.lower()))
    return key


def discover_log_files(folder, pattern):
    files = []
    for path in folder.glob(pattern):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        files.append(path)
    return sorted(files, key=natural_sort_key)


def load_summaries(folder, pattern, epcs):
    file_summaries = []
    for log_file in discover_log_files(folder, pattern):
        records = read_log_file(log_file)
        summary = summarize_by_epc(records, epcs)
        has_selected_data = any(summary[epc]["rssi_values"] for epc in epcs)
        if has_selected_data:
            file_summaries.append((log_file, summary))
    return file_summaries


def make_plot(folder, pattern, epcs, output_path=None, show=False, title=None):
    plt, Patch = import_matplotlib()
    file_summaries = load_summaries(folder, pattern, epcs)

    if not file_summaries:
        raise SystemExit("No matching EPC readings were found in the selected folder.")

    file_labels = [log_file.stem for log_file, _summary in file_summaries]
    group_positions = list(range(1, len(file_summaries) + 1))
    colors = ACADEMIC_COLORS
    tag_labels = make_tag_labels(epcs)

    fig, (ax_rssi, ax_count) = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(4.5, 4.1),
        sharex=True,
        constrained_layout=True,
        gridspec_kw={"height_ratios": [2.1, 1]},
    )

    group_width = 0.78
    box_width = min(0.22, group_width / max(len(epcs), 1) * 0.75)
    offsets = [
        (index - (len(epcs) - 1) / 2) * (group_width / max(len(epcs), 1))
        for index in range(len(epcs))
    ]

    legend_items = []
    for epc_index, epc in enumerate(epcs):
        color = colors[epc_index % len(colors)]
        box_style = boxplot_style(color)
        box_data = []
        box_positions = []

        for file_index, (_log_file, summary) in enumerate(file_summaries):
            rssi_values = summary[epc]["rssi_values"]
            if not rssi_values:
                continue
            box_data.append(rssi_values)
            box_positions.append(group_positions[file_index] + offsets[epc_index])

        if box_data:
            boxplot = ax_rssi.boxplot(
                box_data,
                positions=box_positions,
                widths=box_width,
                patch_artist=True,
                manage_ticks=False,
                **box_style,
            )
            for patch in boxplot["boxes"]:
                patch.set_alpha(0.62)

        legend_items.append(
            Patch(facecolor=color, alpha=0.62, label=tag_labels[epc_index])
        )

        read_counts = [
            summary[epc]["total_read_count"] for _log_file, summary in file_summaries
        ]
        ax_count.plot(
            group_positions,
            read_counts,
            color=color,
            marker="o",
            markerfacecolor="white",
            markeredgewidth=1.0,
            markersize=3.6,
            label=tag_labels[epc_index],
        )

    if title:
        ax_rssi.set_title(title, pad=5)
    ax_rssi.set_ylabel("RSSI (dBm)")
    style_axis(ax_rssi)
    ax_rssi.legend(
        handles=legend_items,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.24 if title else 1.10),
        ncol=min(3, len(epcs)),
        frameon=False,
    )

    ax_count.set_xlabel("Log file")
    ax_count.set_ylabel("Total read count")
    ax_count.set_ylim(bottom=0)
    style_axis(ax_count)
    ax_count.set_xticks(group_positions)
    ax_count.set_xticklabels(file_labels, rotation=25, ha="right")
    print_tag_mapping(epcs)

    if output_path is None:
        output_path = folder / "rfid_folder_summary.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    print(f"Saved plot to {output_path.resolve()}")

    if show:
        plt.show()
    else:
        plt.close(fig)


def main():
    args = parse_args()
    folder = Path(args.folder).expanduser()
    output_path = Path(args.output).expanduser() if args.output else None
    make_plot(
        folder=folder,
        pattern=args.pattern,
        epcs=args.epcs,
        output_path=output_path,
        show=not args.noshow,
        title=args.title,
    )


if __name__ == "__main__":
    main()
