"""=============================================================================
ADVANCED 3D INTERACTIVE CLUSTER & QUERY RETRIEVAL (PLOTLY)
=============================================================================
This script reduces 384-D embeddings to 3D coordinates using PCA, then generates 
an interactive 3D HTML plot allowing you to rotate the semantic space, inspect 
chunks, and see live K=5 nearest neighbor retrieval in action.
============================================================================="""

import pickle
import numpy as np
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist

def generate_interactive_3d_plot(live_query=None, k_neighbors=5):
    print("--- Generating Interactive 3D Semantic Cluster Map ---")

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
    print("[+] Encoding chunks into 384-D vectors...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)

    # 3. Fit PCA to reduce 384 dimensions down to 3D coordinates
    print("[+] Applying PCA for 3D dimensionality reduction...")
    pca = PCA(n_components=3, random_state=42)
    coords_3d = pca.fit_transform(embeddings)

    # 4. Initialize Plotly Figure
    fig = go.Figure()

    # Get unique source files for distinct coloring
    unique_sources = sorted(list(set(sources)))
    
    # Plot each knowledge base file as its own 3D scatter trace
    for src in unique_sources:
        mask = [s == src for s in sources]
        subset_coords = coords_3d[mask]
        subset_texts = [texts[i] for i, m in enumerate(mask) if m]
        
        # Format hover text for each chunk pin
        hover_texts = [f"<b>File:</b> {src}<br><b>Chunk:</b> {t[:120]}..." for t in subset_texts]

        fig.add_trace(go.Scatter3d(
            x=subset_coords[:, 0],
            y=subset_coords[:, 1],
            z=subset_coords[:, 2],
            mode='markers',
            name=src,
            text=hover_texts,
            hoverinfo='text',
            marker=dict(size=7, opacity=0.85)
        ))

    # 5. Optional: Plot a live query and its K={k_neighbors} nearest neighbors in 3D
    if live_query:
        print(f"[+] Plotting live query in 3D: '{live_query}'")
        query_emb = model.encode([live_query])
        query_3d = pca.transform(query_emb) # Project query into the same 3D PCA space

        # Find K={k_neighbors} nearest neighbors in true 384-D space
        distances = cdist(query_emb, embeddings, metric='euclidean')[0]
        k_indices = np.argsort(distances)[:k_neighbors]
        neighbor_coords = coords_3d[k_indices]

        # A. Add the Live Query as a giant red diamond/star marker
        fig.add_trace(go.Scatter3d(
            x=query_3d[:, 0],
            y=query_3d[:, 1],
            z=query_3d[:, 2],
            mode='markers',
            name="[LIVE] User Query",
            text=[f"<b>QUERY:</b> {live_query}"],
            hoverinfo='text',
            marker=dict(size=12, color='red', symbol='diamond', line=dict(color='black', width=1))
        ))

        # B. Draw 3D lines connecting the query to its K={k_neighbors} nearest neighbor chunks
        for nc in neighbor_coords:
            fig.add_trace(go.Scatter3d(
                x=[query_3d[0, 0], nc[0]],
                y=[query_3d[0, 1], nc[1]],
                z=[query_3d[0, 2], nc[2]],
                mode='lines',
                line=dict(color='red', width=3, dash='dash'),
                showlegend=False,
                hoverinfo='none'
            ))

    # 6. Layout configuration for a sleek dashboard presentation
    fig.update_layout(
        title=f"<b>Interactive 3D Semantic Knowledge Base & K={k_neighbors} RAG Retrieval</b>",
        scene=dict(
            xaxis_title="Principal Component 1",
            yaxis_title="Principal Component 2",
            zaxis_title="Principal Component 3"
        ),
        legend=dict(title="Documentation Sources", itemsizing='constant'),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    # Save as an interactive HTML file
    output_html = f"vector_clusters_3d_k{k_neighbors}.html"
    fig.write_html(output_html)
    print(f"[+] Success! Interactive 3D map saved as '{output_html}'. Open it in any browser!")
    
    # Automatically open in your default browser
    fig.show()

if __name__ == "__main__":
    sample_test_query = "JavaScript loading chunk failed and API requests hang with Gateway Timeout"
    generate_interactive_3d_plot(live_query=sample_test_query, k_neighbors=3)