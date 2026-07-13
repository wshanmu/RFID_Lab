import argparse
from pathlib import Path

from rfid_log_utils import read_log_file, summarize_by_epc
from rfid_plot_style import (
    READ_COUNT_COLOR,
    apply_academic_style,
    boxplot_style,
    make_tag_labels,
    print_tag_mapping,
    style_axis,
)


def import_matplotlib():
    try:
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch
    except ImportError as exc:
        raise SystemExit(
            "matplotlib is required for plotting. Install it with: python3 -m pip install matplotlib"
        ) from exc
    apply_academic_style(plt)
    return plt, Line2D, Patch


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot RSSI distribution and total read count for selected EPCs in one log file."
    )
    parser.add_argument("--log-file", required=True, help="Path to one RFID log file.")
    parser.add_argument(
        "--epcs",
        nargs="+",
        required=True,
        help="EPC values to include in the plot.",
    )
    parser.add_argument(
        "--output",
        help="Output image path. Default: <log-file-name>_summary.png",
    )
    parser.add_argument("--noshow", action="store_true", help="Not Display the plot window.")
    parser.add_argument("--title", help="Optional plot title.")
    return parser.parse_args()


def make_plot(log_file, epcs, output_path=None, show=False, title=None):
    plt, Line2D, Patch = import_matplotlib()
    records = read_log_file(log_file)
    summary = summarize_by_epc(records, epcs)
    tag_labels = make_tag_labels(epcs)

    positions = list(range(1, len(epcs) + 1))
    box_positions = []
    box_data = []
    total_counts = []

    for index, epc in enumerate(epcs, start=1):
        rssi_values = summary[epc]["rssi_values"]
        total_counts.append(summary[epc]["total_read_count"])
        if rssi_values:
            box_positions.append(index)
            box_data.append(rssi_values)

    if not box_data:
        raise SystemExit("No matching EPC readings were found in the log file.")

    fig, ax_rssi = plt.subplots(constrained_layout=True)
    box_facecolor = "#DCEAF7"
    box_style = boxplot_style(box_facecolor)
    ax_rssi.boxplot(
        box_data,
        positions=box_positions,
        widths=0.38,
        patch_artist=True,
        **box_style,
    )

    if title:
        ax_rssi.set_title(title, pad=5)
    ax_rssi.set_xlabel("Tag")
    ax_rssi.set_ylabel("RSSI (dBm)")
    ax_rssi.set_xticks(positions)
    ax_rssi.set_xticklabels(tag_labels)
    ax_rssi.margins(x=0.08)
    style_axis(ax_rssi)

    ax_count = ax_rssi.twinx()
    ax_count.plot(
        positions,
        total_counts,
        color=READ_COUNT_COLOR,
        marker="o",
        markerfacecolor="white",
        markeredgewidth=1.1,
        markersize=3.8,
        label="Total read count",
    )
    ax_count.set_ylabel("Total read count")
    style_axis(ax_count, grid_axis=None, show_right_spine=True)
    ax_count.spines["left"].set_visible(False)
    ax_count.tick_params(axis="y", labelcolor=READ_COUNT_COLOR)
    ax_count.yaxis.label.set_color(READ_COUNT_COLOR)

    legend_handles = [
        Patch(facecolor=box_facecolor, edgecolor="#222222", label="RSSI distribution"),
        Line2D(
            [0],
            [0],
            color=READ_COUNT_COLOR,
            marker="o",
            markerfacecolor="white",
            label="Total read count",
        ),
    ]
    ax_rssi.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.26 if title else 1.13),
        ncol=2,
        frameon=False,
    )
    print_tag_mapping(epcs)

    if output_path is None:
        output_path = log_file.with_name(f"{log_file.stem}_summary.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    print(f"Saved plot to {output_path.resolve()}")

    if show:
        plt.show()
    else:
        plt.close(fig)


def main():
    args = parse_args()
    log_file = Path(args.log_file).expanduser()
    output_path = Path(args.output).expanduser() if args.output else None
    make_plot(
        log_file=log_file,
        epcs=args.epcs,
        output_path=output_path,
        show=not args.noshow,
        title=args.title,
    )


if __name__ == "__main__":
    main()
