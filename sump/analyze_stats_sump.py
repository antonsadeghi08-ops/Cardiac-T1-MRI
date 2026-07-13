import pandas as pd
import matplotlib.pyplot as plt
import mplcursors

VALID_METHODS = ['ecv', 'lge', 't1', 't1rho', 't2']


def get_input(prompt, valid_options=None):
    while True:
        val = input(prompt).strip().lower()
        if valid_options is None or val in valid_options:
            return val
        print(f"  Ogiltigt val. Välj bland: {', '.join(valid_options)}")


def plot_scatter(csv_path):
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['mu_roi', 'mu_ref', 'sigma_roi', 'sigma_ref'])

    method_map = {0: 'ecv', 1: 'lge', 2: 't1', 3: 't1rho', 4: 't2'}
    if df['method'].dtype != object:
        df['method'] = df['method'].map(method_map)

    print(f"\nTillgängliga metoder: {', '.join(VALID_METHODS)}")
    method_x = get_input("Välj metod för X-axeln: ", VALID_METHODS)
    method_y = get_input("Välj metod för Y-axeln: ", VALID_METHODS)

    df_x = df[df['method'] == method_x][['patient', 'slice', 'mu_roi', 'mu_ref']].rename(
        columns={'mu_roi': 'x_roi', 'mu_ref': 'x_ref'})
    df_y = df[df['method'] == method_y][['patient', 'slice', 'mu_roi', 'mu_ref']].rename(
        columns={'mu_roi': 'y_roi', 'mu_ref': 'y_ref'})

    merged = pd.merge(df_x, df_y, on=['patient', 'slice'])

    merged_roi = merged.dropna(subset=['x_roi', 'y_roi'])
    merged_ref = merged.dropna(subset=['x_ref', 'y_ref'])

    if merged_roi.empty and merged_ref.empty:
        print("Ingen matchande data hittades.")
        return

    fig, ax = plt.subplots(figsize=(8, 7))

    scatter_roi = ax.scatter(merged_roi['x_roi'], merged_roi['y_roi'], s=60,
                             color='steelblue', alpha=0.7, edgecolors='white',
                             linewidths=0.5, label='ROI')
    scatter_ref = ax.scatter(merged_ref['x_ref'], merged_ref['y_ref'], s=60,
                             color='darkorange', alpha=0.7, edgecolors='white',
                             linewidths=0.5, label='Ref')

    ax.set_xlabel(f"{method_x} (average)")
    ax.set_ylabel(f"{method_y} (average)")
    ax.set_title(f"{method_x} vs {method_y}: ROI & Ref")
    ax.set_facecolor('#f8f9fa')
    ax.legend(title="Type", loc='best')
    fig.tight_layout()

    labels_roi = [
        f"ROI - Patient {int(row.patient)}, Slice {int(row.slice)}\n{method_x}: {row.x_roi:.3f}\n{method_y}: {row.y_roi:.3f}"
        for row in merged_roi.itertuples()
    ]
    labels_ref = [
        f"Ref - Patient {int(row.patient)}, Slice {int(row.slice)}\n{method_x}: {row.x_ref:.3f}\n{method_y}: {row.y_ref:.3f}"
        for row in merged_ref.itertuples()
    ]

    cursor = mplcursors.cursor([scatter_roi, scatter_ref], hover=True)

    @cursor.connect("add")
    def on_add(sel):
        if sel.artist == scatter_roi:
            sel.annotation.set_text(labels_roi[sel.index])
        else:
            sel.annotation.set_text(labels_ref[sel.index])
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

    print(
        f"\nPlottade {len(merged_roi)} ROI-punkter och {len(merged_ref)} Ref-punkter.")
    plt.show()


csv_path = "/Users/Anton_Sadeghi/Desktop/data_sorted.csv"
plot_scatter(csv_path)

# /Users/Anton_Sadeghi/Desktop/data_sorted.csv
