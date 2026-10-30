"""=============================================================================
ADVANCED 2D VECTOR CLUSTER & QUERY RETRIEVAL VISUALIZATION
=============================================================================
1. Visualizes all 12 knowledge base files using 12 unique colors and shapes.
2. Embeds a sample query, plots it as a giant red star, and highlights 
   its K=3 nearest neighbor chunks with a circle.
============================================================================="""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist

def generate_cluster_plot(live_query=None, k_neig=3):
    print("--- Generating Advanced Semantic Cluster Map ---")

    # 1. Load metadata containing text chunks and source files
    metadata_path = "utils/chunk_metadata.pkl"
    try:
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
    except FileNotFoundError:
        print(f"[-] Error: {metadata_path} not found. Build your index first!")
        return

    texts = [chunk["text"] for chunk in metadata]
    sources = [chunk["source_file"] for chunk in metadata]

    # 2. Encode chunks into 384-D vectors
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)

    # 3. Fit PCA to reduce 384 dimensions down to 2D coordinates
    pca = PCA(n_components=2, random_state=42)
    coords_2d = pca.fit_transform(embeddings)

    # 4. Set up a distinct palette of 12 unique colors and list of shapes (markers)
    unique_sources = sorted(list(set(sources)))
    palette = sns.color_palette("husl", len(unique_sources)) # Generates distinct hues
    markers = ['o', 's', '^', 'D', 'P', 'X', 'v', '<', '>', 'p', '*', 'h']
    
    source_to_style = {
        src: {"color": palette[i], "marker": markers[i % len(markers)]}
        for i, src in enumerate(unique_sources)
    }

    # 5. Plotting setup
    plt.figure(figsize=(13, 9))
    sns.set_theme(style="whitegrid")

    # Plot each source file separately to assign custom markers & colors
    for src in unique_sources:
        mask = [s == src for s in sources]
        plt.scatter(
            coords_2d[mask, 0],
            coords_2d[mask, 1],
            c=[source_to_style[src]["color"]],
            marker=source_to_style[src]["marker"],
            label=src,
            s=110,
            alpha=0.85,
            edgecolors="black",
            linewidths=0.6
        )

    # 6. Optional: Plot a live query and its K=3 nearest neighbors
    if live_query:
        print(f"[+] Plotting live query: '{live_query}'")
        query_emb = model.encode([live_query])
        query_2d = pca.transform(query_emb) # Project query into the same 2D PCA space

        # Find K={k_neig} nearest neighbors using Euclidean distance in 2D space (or high-D space)
        distances = cdist(query_emb, embeddings, metric='euclidean')[0]
        k_indices = np.argsort(distances)[:k_neig]

        # Plot query as a giant red star
        plt.scatter(
            query_2d[:, 0], query_2d[:, 1],
            c='red', marker='*', s=350, zorder=5,
            edgecolors='black', linewidths=1.2,
            label="[LIVE] User Query"
        )

        # Draw connecting lines and circle around the K={k_neig} nearest neighbors
        neighbor_coords = coords_2d[k_indices]
        for nc in neighbor_coords:
            plt.plot([query_2d[0, 0], nc[0]], [query_2d[0, 1], nc[1]], 'k--', alpha=0.5, linewidth=1)

        # Draw a bounding circle enclosing the k_neig nearest points
        max_dist = max([np.linalg.norm(query_2d[0] - nc) for nc in neighbor_coords])
        circle = plt.Circle((query_2d[0, 0], query_2d[0, 1]), max_dist * 1.05, color='red', fill=False, linestyle='--', linewidth=2, label=f"K={k_neig} Retrieval Radius")
        plt.gca().add_patch(circle)

    plt.title(f"Semantic Cluster Map & K={k_neig} RAG Retrieval Visualization", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("Principal Component 1 (Semantic Axis)", fontsize=11)
    plt.ylabel("Principal Component 2 (Semantic Axis)", fontsize=11)
    
    # Clean legend positioning outside the plot
    plt.legend(title="Knowledge Base & Query", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    plt.tight_layout()

    output_image = f"vector_clusters_interactive_k{k_neig}.png"
    plt.savefig(output_image, dpi=300)
    print(f"[+] Visualization successfully saved as '{output_image}'.")
    plt.show()

if __name__ == "__main__":
    # Test it with a sample multi-intent or specific query!
    sample_test_query = "JavaScript loading chunk failed and API requests hang with Gateway Timeout"
    generate_cluster_plot(live_query=sample_test_query, k_neig=3)