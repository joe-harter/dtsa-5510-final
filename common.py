import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns

# Offensive Lineman are all grey because they don't tend to line up in different positions so I want to visualize them all the same
COLOR_MAPPING = color_mapping = {
    "WR": "purple",
    "C": "grey",
    "T": "grey",
    "G": "grey",
    "QB": "red",
    "RB": "orange",
    "FB": "green",
    "TE": "blue",
}


def map_labels_to_plays(labels, df):
    labeled_indexes = list(zip(labels, df.index.to_list()))

    # Map the zipped list to a map of key=cluster label and values = all game/playids for that label
    map = {}
    for label, index in labeled_indexes:
        if map.get(label) is None:
            map[label] = [index]
        else:
            l = map[label]
            l.append(index)
            map[label] = l
    return map


def plot_clusters(model_df, off_df, label_map, cluster_name, show_means=True):
    # Won't plot in the notebook, but will save to a file
    matplotlib.use("Agg")

    # Display a scatterplot of every player's position on the field
    plot_height = len(label_map.keys()) * 4
    f, axs = plt.subplots(
        int(len(label_map.keys()) / 2),
        2,
        figsize=(12, plot_height),
        gridspec_kw=dict(width_ratios=[3, 3]),
    )

    sorted_counts = sorted(label_map.items(), key=lambda x: len(x[1]), reverse=True)
    one_play_clusters = []
    for i, (k, indexes) in enumerate(sorted_counts):
        if len(indexes) == 1:
            one_play_clusters.append(f"cluster: {k} index:{indexes[0]}")
        # Get the indexes of the plays for this cluster
        slice_df = off_df.loc[indexes]
        means = model_df[model_df.index.isin(indexes)].mean()
        sns.scatterplot(
            slice_df[~(slice_df["position"] == "C")],
            x="rel_x_c",
            y="rel_y_c",
            s=30,
            hue="position",
            ax=axs[int(i / 2)][(i + 1) % 2],
            palette=COLOR_MAPPING,
        )
        sns.scatterplot(
            slice_df[slice_df["position"] == "C"],
            x="rel_x_c",
            y="rel_y_c",
            s=30,
            marker="s",
            hue="position",
            ax=axs[int(i / 2)][(i + 1) % 2],
            palette=COLOR_MAPPING,
        )

        axs[int(i / 2)][(i + 1) % 2].set_ylim(-25, 25)
        axs[int(i / 2)][(i + 1) % 2].set_xlim(-1, 10)
        top = 25

        # Only the smaller model makes sense to include this metadata
        if show_means:
            wr_count = means["wr_count"]
            te_count = means["te_count"]
            qb_x = means["qb_x"]
            blocker_count = means["blocker_count"]

            axs[int(i / 2)][(i + 1) % 2].text(
                0,
                top + 1,
                f"{k} - {len(indexes)} plays.\nWR Count: {wr_count}\nTE Count: {te_count}\nQB Position: {qb_x}\nBlocker Count: {blocker_count}",
                horizontalalignment="left",
                verticalalignment="bottom",
                wrap=True,
            )
    f.tight_layout()
    f.savefig(f"./output/{cluster_name}.png", dpi=300)
    pd.DataFrame.from_dict(one_play_clusters).to_csv(
        f"./output/{cluster_name}-one_play_clusters.csv"
    )
