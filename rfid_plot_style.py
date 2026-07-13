ACADEMIC_COLORS = [
    "#0072B2",
    "#D55E00",
    "#009E73",
    "#CC79A7",
    "#E69F00",
    "#56B4E9",
]
READ_COUNT_COLOR = "#D55E00"
TEXT_COLOR = "#222222"
GRID_COLOR = "#D0D0D0"
SPINE_COLOR = "#5F6368"


def apply_academic_style(plt):
    plt.rcParams.update(
        {
            "font.size": 11,
            "figure.figsize": (4.5, 2.8),
            "axes.labelsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "lines.linewidth": 1.0,
            "axes.linewidth": 0.8,
            "savefig.bbox": "tight",
            "savefig.dpi": 300,
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "axes.titlesize": 10,
            "axes.labelcolor": TEXT_COLOR,
            "legend.title_fontsize": 10,
            "patch.linewidth": 0.9,
            "axes.edgecolor": SPINE_COLOR,
        }
    )


def make_tag_labels(epcs):
    return [f"Tag {index}" for index, _epc in enumerate(epcs, start=1)]


def print_tag_mapping(epcs):
    print("Tag label mapping:")
    for label, epc in zip(make_tag_labels(epcs), epcs):
        print(f"  {label}: {epc}")


def style_axis(ax, grid_axis="y", show_right_spine=False):
    ax.set_axisbelow(True)
    if grid_axis:
        ax.grid(
            True,
            axis=grid_axis,
            color=GRID_COLOR,
            linestyle="--",
            linewidth=0.45,
            alpha=0.75,
        )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(show_right_spine)
    for spine_name in ("left", "bottom", "right"):
        ax.spines[spine_name].set_color(SPINE_COLOR)
        ax.spines[spine_name].set_linewidth(0.8)
    ax.tick_params(axis="both", color=SPINE_COLOR, labelcolor=TEXT_COLOR, width=0.8)


def boxplot_style(facecolor):
    return {
        "boxprops": {
            "facecolor": facecolor,
            "edgecolor": "#222222",
            "linewidth": 0.9,
        },
        "medianprops": {"color": "#111111", "linewidth": 1.0},
        "whiskerprops": {"color": "#333333", "linewidth": 0.9},
        "capprops": {"color": "#333333", "linewidth": 0.9},
        "flierprops": {
            "marker": "o",
            "markerfacecolor": "white",
            "markeredgecolor": "#555555",
            "markersize": 2.4,
            "alpha": 0.65,
        },
        "meanprops": {
            "marker": "D",
            "markerfacecolor": "white",
            "markeredgecolor": "#111111",
            "markersize": 4,
        },
    }
