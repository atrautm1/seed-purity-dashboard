import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from pathlib import Path
import logging
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr

logger = logging.getLogger(__name__)


def generate_test_df():
    np.random.seed(42)
    n_markers, n_lines = 500, 30
    df = pd.DataFrame(
        np.random.rand(n_markers, n_lines),
        index=[f"SNP_{i}" for i in range(1, n_markers + 1)],
        columns=[f"Line_{i}" for i in range(1, n_lines + 1)],
    )
    return df


def plotly_output(loading_df, n_keep):
    # 1. Split data by status for distinct Plotly series
    removed_df = loading_df[loading_df["Status"] == "Removed"]
    kept_df = loading_df[loading_df["Status"] == "Kept"]

    # 2. Get the threshold radius
    threshold_radius = float(loading_df.iloc[n_keep]["Importance"])

    # 3. Define the traces (Series 1: Removed, Series 2: Kept)
    trace_removed = {
        "x": removed_df["PC1_Loading"].tolist(),
        "y": removed_df["PC2_Loading"].tolist(),
        "mode": "markers",
        "type": "scatter",
        "name": "Removed (Low Impact)",
        "marker": {"color": "lightgray", "size": 6, "opacity": 0.6},
    }

    trace_kept = {
        "x": kept_df["PC1_Loading"].tolist(),
        "y": kept_df["PC2_Loading"].tolist(),
        "mode": "markers",
        "type": "scatter",
        "name": "Kept (High Impact)",
        "marker": {"color": "blue", "size": 10, "line": {"color": "black", "width": 1}},
    }

    # 4. Define Plotly shapes for crosshairs and the threshold circle
    shapes = [
        # Horizontal crosshair at y=0 (replaces plt.axhline)
        {
            "type": "line",
            "x0": 0,
            "x1": 1,
            "xref": "paper",
            "y0": 0,
            "y1": 0,
            "yref": "y",
            "line": {"color": "black", "width": 1, "dash": "dash"},
        },
        # Vertical crosshair at x=0 (replaces plt.axvline)
        {
            "type": "line",
            "x0": 0,
            "x1": 0,
            "xref": "x",
            "y0": 0,
            "y1": 1,
            "yref": "paper",
            "line": {"color": "black", "width": 1, "dash": "dash"},
        },
        # Selection threshold circle (replaces plt.Circle)
        {
            "type": "circle",
            "x0": -threshold_radius,
            "x1": threshold_radius,
            "y0": -threshold_radius,
            "y1": threshold_radius,
            "line": {"color": "red", "width": 2, "dash": "dot"},
        },
    ]

    # 5. Build the final graph payload dictionary
    graph_payload = {
        "id": "pca",
        "title": "PCA",
        "data": [trace_removed, trace_kept],
        "layout": {
            "title": "PCA Marker Loadings: Kept vs. Removed",
            "xaxis": {
                "title": {"text": "Impact on Principal Component 1"},
                "zeroline": False,
                "showgrid": True,
                "gridcolor": "rgba(0,0,0,0.1)",
                "automargin": True,
            },
            "yaxis": {
                "title": {"text": "Impact on Principal Component 2"},
                "zeroline": False,
                "showgrid": True,
                "gridcolor": "rgba(0,0,0,0.1)",
                "automargin": True,
            },
            "shapes": shapes,
            "legend": {"x": 0.8, "y": 1},
            "margin": {"t": 50, "l": 50, "r": 30, "b": 50},
        },
    }

    return graph_payload


def run_pca_and_select_markers(df, n_keep=0.8, filePrefix="", outputDir=None):
    """
    Run PCA on the SNP proportion data and select the top markers based on their importance.

    Parameters:
    - df: DataFrame with Markers as rows and Lines as columns.
    - n_keep: Proportion of top markers to keep based on PCA loadings.

    Returns:
    - kept_markers: List of markers to keep for UMAP.
    - loading_df: DataFrame containing marker loadings and importance scores.
    """
    # Transpose and standardize
    # For feature selection, PCA needs Lines as rows and Markers as columns (features)
    data_t = df.T

    # # Standardize the markers so they are on the same scale
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_t)

    # Run PCA
    # We will use the top 2 PCs to capture the primary variance drivers
    pca = PCA(n_components=2, random_state=42)
    pca.fit(scaled_data)

    # Calculate Marker Importance (Loadings)
    # The "components_" are the weights (loadings) of each marker on the PCs
    pc1_loadings = pca.components_[0]
    pc2_loadings = pca.components_[1]

    # Overall importance is the distance from the origin (0,0) in the loading plot
    # We use the Pythagorean theorem: sqrt(a^2 + b^2)
    importance_scores = np.sqrt(pc1_loadings**2 + pc2_loadings**2)

    loading_df = pd.DataFrame(
        {
            "Marker": df.index,
            "PC1_Loading": pc1_loadings,
            "PC2_Loading": pc2_loadings,
            "Importance": importance_scores,
        }
    )

    # Determine how many markers to keep for UMAP
    n_keep = int(n_keep * len(df))

    # Sort by importance and slice the top N
    loading_df = loading_df.sort_values(by="Importance", ascending=False)
    kept_markers = loading_df.head(n_keep)["Marker"].tolist()
    # Add a status column for the graph
    loading_df["Status"] = [
        "Kept" if m in kept_markers else "Removed" for m in loading_df["Marker"]
    ]
    if outputDir:
        # Graphical Output (The "Why")
        plt.figure(figsize=(10, 8))

        # Plot the 'Removed' markers in gray
        sns.scatterplot(
            data=loading_df[loading_df["Status"] == "Removed"],
            x="PC1_Loading",
            y="PC2_Loading",
            color="lightgray",
            alpha=0.6,
            s=50,
            label="Removed (Low Impact)",
        )

        # Plot the 'Kept' markers in blue
        sns.scatterplot(
            data=loading_df[loading_df["Status"] == "Kept"],
            x="PC1_Loading",
            y="PC2_Loading",
            color="blue",
            edgecolor="black",
            s=100,
            label="Kept (High Impact)",
        )

        # Draw crosshairs at the origin (0,0)
        plt.axhline(0, color="black", linestyle="--", alpha=0.5)
        plt.axvline(0, color="black", linestyle="--", alpha=0.5)

        # Add a circle to visually show the cutoff threshold
        threshold_radius = loading_df.iloc[n_keep]["Importance"]
        circle = plt.Circle(
            (0, 0),
            threshold_radius,
            color="red",
            fill=False,
            linestyle=":",
            linewidth=2,
            label="Selection Threshold",
        )
        plt.gca().add_patch(circle)

        plt.title("PCA Marker Loadings: Kept vs. Removed")
        plt.xlabel("Impact on Principal Component 1")
        plt.ylabel("Impact on Principal Component 2")
        plt.legend(loc="upper right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            Path(outputDir).joinpath(f"{filePrefix}_pca_marker_selection.png"), dpi=300
        )
        plt.close()
    else:
        graph_output = plotly_output(loading_df, n_keep)

    # Final output ready for UMAP (Still formatted as Markers on Rows, Lines on Cols)
    umap_ready_df = df.loc[kept_markers]

    distances_full = pdist(df.T, metric="euclidean")
    distances_reduced = pdist(umap_ready_df.T, metric="euclidean")

    r, p_value = pearsonr(distances_full, distances_reduced)

    # R-squared represents the proportion of variance retained
    r_squared = r**2
    variance_kept_pct = r_squared * 100

    logger.info(f"Structural Variance Retained: {variance_kept_pct:.2f}%")

    # Calculate Retained Variance
    # Square the loadings to get the proportional variance contribution (sum = 1.0)
    loading_df["PC1_Var_Contribution"] = loading_df["PC1_Loading"] ** 2
    loading_df["PC2_Var_Contribution"] = loading_df["PC2_Loading"] ** 2

    # Filter down to just the kept markers
    kept_df = loading_df[loading_df["Status"] == "Kept"]

    # Calculate the percentage of variance retained within each PC
    pc1_retained = kept_df["PC1_Var_Contribution"].sum() * 100
    pc2_retained = kept_df["PC2_Var_Contribution"].sum() * 100

    # Get the actual variance explained by PC1 and PC2 from the PCA model
    pc1_actual_var = pca.explained_variance_ratio_[0]
    pc2_actual_var = pca.explained_variance_ratio_[1]
    total_pca_var = pc1_actual_var + pc2_actual_var

    # Calculate the overall retained variance in your 2D space (weighted by PC importance)
    overall_retained = (
        (
            (kept_df["PC1_Var_Contribution"].sum() * pc1_actual_var)
            + (kept_df["PC2_Var_Contribution"].sum() * pc2_actual_var)
        )
        / total_pca_var
        * 100
    )

    logger.info("--- Variance Retention Report ---")
    logger.info(f"Total Markers Kept: {len(kept_df)} out of {len(loading_df)}")
    logger.info(f"Variance Retained in PC1: {pc1_retained:.1f}%")
    logger.info(f"Variance Retained in PC2: {pc2_retained:.1f}%")
    logger.info(f"Overall Variance Retained in PCA Space: {overall_retained:.1f}%")
    return umap_ready_df, pca, graph_output
