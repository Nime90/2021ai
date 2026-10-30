"""=============================================================================
STEPS 5 & 6: INTERACTIVE STREAMLIT CHAT APPLICATION (with Test Dataset Selector)
=============================================================================
This script runs a web-based chat interface for our Back-Office Support AI.
Includes an option to select from the evaluation test cases in 'test_dataset.json'
and interactive 3D semantic cluster visualization.

To run this app, open your terminal and type:
    streamlit run app.py
============================================================================="""

import streamlit as st
import os
import sys
import json
import random
import glob
import pickle
import numpy as np
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist

# Add the current directory to Python path so it can find the 'utils' folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.rag_engine import SupportRAGEngine

# =============================================================================
# 1. PAGE CONFIGURATION & STYLING
# =============================================================================
st.set_page_config(
    page_title="Back-Office Support AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Application Header for Management & Stakeholders
st.title("🤖 Back-Office Support AI Assistant")
st.markdown(
    "**Empowering support teams with instant, grounded technical guidance.** "
    "Ask any software troubleshooting question below, or select from the pre-evaluated "
    "golden test suite in the sidebar."
)

# =============================================================================
# 2. LOAD RAG ENGINE & CACHED 3D RESOURCES
# =============================================================================
@st.cache_resource
def initialize_rag_system():
    print("[Streamlit] Initializing RAG Engine for the first time...")
    try:
        engine = SupportRAGEngine()
        return engine
    except Exception as e:
        st.error(f"Failed to initialize RAG Engine: {e}")
        return None

rag_engine = initialize_rag_system()

if not rag_engine:
    st.stop()

@st.cache_resource
def get_cached_3d_pca_data():
    """Computes and caches 3D PCA coordinates and embeddings once for instant 3D rendering."""
    metadata_path = "utils/chunk_metadata.pkl"
    if not os.path.exists(metadata_path):
        return None, None, None
        
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
        
    texts = [chunk["text"] for chunk in metadata]
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)
    
    pca = PCA(n_components=3, random_state=42)
    coords_3d = pca.fit_transform(embeddings)
    
    return metadata, embeddings, coords_3d

# =============================================================================
# 3. LOAD EVALUATION TEST DATASET (CACHED)
# =============================================================================
@st.cache_data
def load_golden_test_cases():
    """Loads evaluation questions from test_dataset.json."""
    json_path = "test_dataset.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

test_cases = load_golden_test_cases()

# =============================================================================
# 3.1 GENERATE KNOWLEDGE BASE QUERIES IN SIDEBAR
# =============================================================================

def generate_dynamic_kb_query():
    """Picks a random markdown file from knowledge_base/ and asks Gemini to invent a realistic user query."""
    kb_files = glob.glob("knowledge_base/*.md")
    if not kb_files:
        return None, None
    
    chosen_file_path = random.choice(kb_files)
    file_name = os.path.basename(chosen_file_path)
    
    with open(chosen_file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        
    prompt = f"""
    You are a software operations manager. Based strictly on the following documentation file ({file_name}), 
    write a realistic, conversational technical support question or ticket description that a back-office agent 
    would submit when encountering this exact issue. Do not include introductory text, just the query.
    
    Documentation Content:
    {file_content[:2000]}
    """
    
    try:
        response = rag_engine.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip(), file_name
    except Exception as e:
        return f"Error generating query: {e}", file_name

# =============================================================================
# 4. INITIALIZE CHAT HISTORY (SESSION STATE)
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hello! I am your Back-Office Support Assistant. How can I help you troubleshoot a technical issue today?",
            "sources": []
        }
    ]

# Manage user input state across interactions
if "selected_query" not in st.session_state:
    st.session_state.selected_query = ""

# =============================================================================
# 5. DISPLAY PAST CHAT MESSAGES
# =============================================================================
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # If the message has cited documentation sources, display them nicely below the text
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Referenced Documentation Sources"):
                for src in message["sources"]:
                    st.caption(f"- `{src}`")
        
        # If this message contains evaluation metadata (from the dynamic generator), display correctness & reasoning
        if "evaluation" in message and message["evaluation"] and message["evaluation"]["expected_file"]:
            eval_data = message["evaluation"]
            status_text = "✅ Correct (Retrieved Target KB)" if eval_data["is_correct"] else "❌ Incorrect (Missed Target KB)"
            with st.expander(f"🧠 Evaluation & Reasoning: {status_text}"):
                st.write(f"**Target Source File (Ground Truth):** `{eval_data['expected_file']}`")
                st.write(f"**Files Retrieved by FAISS:** `{message['sources']}`")
                st.caption(
                    "**Reasoning Breakdown:** The system verified whether vector similarity successfully "
                    "isolated the precise documentation file that inspired the generated query, validating retrieval precision."
                )

        # Render 3D Visualizer Expander for Assistant Messages (skipped for initial welcome greeting)
        if message["role"] == "assistant" and idx > 0:
            with st.expander("📈 Visualize Query in 3D Semantic Space ($K=5$)"):
                st.caption("Rotating 3D PCA projection of the 384-D vector space showing query position and retrieval radius.")
                
                # Fetch corresponding user query from the previous message index
                target_query = st.session_state.messages[idx - 1]["content"]
                
                metadata, embeddings, coords_3d = get_cached_3d_pca_data()
                if metadata is not None:
                    model = SentenceTransformer("all-MiniLM-L6-v2")
                    query_emb = model.encode([target_query])
                    
                    pca = PCA(n_components=3, random_state=42)
                    pca.fit(embeddings)
                    query_3d = pca.transform(query_emb)
                    
                    distances = cdist(query_emb, embeddings, metric='euclidean')[0]
                    k_indices = np.argsort(distances)[:5]
                    neighbor_coords = coords_3d[k_indices]
                    
                    fig = go.Figure()
                    unique_sources = sorted(list(set([m["source_file"] for m in metadata])))
                    
                    for src in unique_sources:
                        mask = [m["source_file"] == src for m in metadata]
                        sub_coords = coords_3d[mask]
                        fig.add_trace(go.Scatter3d(
                            x=sub_coords[:, 0], y=sub_coords[:, 1], z=sub_coords[:, 2],
                            mode='markers', name=src, marker=dict(size=5, opacity=0.7)
                        ))
                        
                    fig.add_trace(go.Scatter3d(
                        x=query_3d[:, 0], y=query_3d[:, 1], z=query_3d[:, 2],
                        mode='markers', name="[Query Star]",
                        marker=dict(size=10, color='red', symbol='diamond', line=dict(color='black', width=1))
                    ))
                    
                    for nc in neighbor_coords:
                        fig.add_trace(go.Scatter3d(
                            x=[query_3d[0, 0], nc[0]], y=[query_3d[0, 1], nc[1]], z=[query_3d[0, 2], nc[2]],
                            mode='lines', line=dict(color='red', width=2, dash='dash'), showlegend=False
                        ))
                        
                    fig.update_layout(
                        height=420,
                        margin=dict(l=0, r=0, b=0, t=20),
                        scene=dict(xaxis_title="PC1", yaxis_title="PC2", zaxis_title="PC3")
                    )
                    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 6. SIDEBAR CONTROLS & GOLDEN TEST CASE SELECTOR
# =============================================================================
with st.sidebar:
    st.header("🛠️ Assistant Controls")
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.selected_query = ""
        st.rerun()
        
    st.markdown("---")
    st.markdown(f"### 📋 Golden Test Suite ({len(test_cases)} Cases)")
    st.markdown("Select a pre-configured test question and click run:")

    if test_cases:
        # Create a dropdown mapping test IDs and questions
        test_options = {f"[{tc['id']}] {tc['question'][:45]}...": tc for tc in test_cases}
        selected_label = st.selectbox("Choose a test case:", ["-- Select a test case --"] + list(test_options.keys()))

        if selected_label != "-- Select a test case --":
            chosen_test = test_options[selected_label]
            
            with st.expander("👁️ View Expected Evaluation Data"):
                st.write(f"**Test ID:** {chosen_test['id']}")
                st.write(f"**Target File(s):** {chosen_test['recommended documentation file']}")
                st.markdown("---")
                st.write(f"**Expected Answer Profile:**\n{chosen_test['recommended answer']}")
            
            # Explicit button to trigger the test case execution without looping
            if st.button("🚀 Run Selected Test Case", use_container_width=True):
                st.session_state.selected_query = chosen_test["question"]
                st.rerun()
    else:
        st.warning("`test_dataset.json` not found in root directory.")

    st.markdown("---")
    st.markdown("### 🎲 Dynamic KB Generator")
    st.markdown("Test the RAG engine with a fresh, AI-generated query based on a random internal runbook:")

    if st.button("Generate & Test Random Runbook"):
        with st.spinner("Generating dynamic support query..."):
            dyn_query, target_file = generate_dynamic_kb_query()
            if dyn_query:
                # Save query and store the target file in session state to verify correctness later
                st.session_state.selected_query = dyn_query
                st.session_state.expected_target_file = target_file
                st.rerun()

    st.markdown("---")
    st.markdown("### 📊 System Specs")
    st.info(
        "**Vector Store:** FAISS (In-Memory)\n\n"
        "**Embedding Model:** `all-MiniLM-L6-v2`\n\n"
        "**LLM:** Gemini 2.5 Flash\n\n"
        "**Corpus:** Technical Markdown KBs"
    )

# =============================================================================
# 7. HANDLE USER INPUT & GENERATE AI RESPONSE
# =============================================================================
user_query = st.chat_input("Type your support question here...")

# If a test case or dynamic query was selected/generated in the sidebar, use it as active query
if st.session_state.selected_query:
    user_query = st.session_state.selected_query
    st.session_state.selected_query = "" # Clear immediately after capturing

if user_query:
    # A. Display user message immediately on the chat interface
    with st.chat_message("user"):
        st.markdown(user_query)
    
    st.session_state.messages.append({"role": "user", "content": user_query})

    # B. Generate AI Response using RAG Engine
    with st.chat_message("assistant"):
        with st.spinner("Searching internal documentation & generating resolution..."):
            result = rag_engine.generate_answer(user_query)
            ai_response = result["answer"]
            sources_used = result["sources"]
            
        st.markdown(ai_response)
        
        if sources_used:
            with st.expander("📚 View Referenced Documentation Sources"):
                for src in sources_used:
                    st.caption(f"- `{src}`")

        # Check if this query came from the dynamic KB generator (stored in session state)
        expected_file = st.session_state.pop("expected_target_file", None)
        evaluation_payload = None
        
        if expected_file:
            is_correct = expected_file in sources_used
            evaluation_payload = {
                "expected_file": expected_file,
                "is_correct": is_correct
            }
            # Show live evaluation feedback right below the response
            status_text = "✅ Correct (Retrieved Target KB)" if is_correct else "❌ Incorrect (Missed Target KB)"
            with st.expander(f"🧠 Evaluation & Reasoning: {status_text}"):
                st.write(f"**Target Source File (Ground Truth):** `{expected_file}`")
                st.write(f"**Files Retrieved by FAISS:** `{sources_used}`")
                st.caption(
                    "**Reasoning Breakdown:** The system verified whether vector similarity successfully "
                    "isolated the precise documentation file that inspired the generated query, validating retrieval precision."
                )

    # C. Save assistant response and evaluation data to session state history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": ai_response,
        "sources": sources_used,
        "evaluation": evaluation_payload
    })
    st.rerun()