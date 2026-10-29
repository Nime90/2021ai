"""=============================================================================
STEP 1: DOCUMENT LOADING, PARSING, AND CHUNKING SCRIPT
=============================================================================
This script reads all the technical markdown files from our 'knowledge_base/' 
folder, splits them into clean contextual blocks (chunks), and prepares them 
to be converted into vector embeddings.

Dependencies required:
    pip install markdown
============================================================================="""

import os
import glob

# Define the folder where our technical markdown files are stored
KNOWLEDGE_BASE_DIR = "knowledge_base"

def load_and_chunk_documents(base_dir=KNOWLEDGE_BASE_DIR):
    """
    Reads every markdown (.md) file in the knowledge base directory, 
    separates them into logical chunks (e.g., split by headers like '## '), 
    and returns a structured list of text chunks with their source file metadata.
    """
    
    # Check if the folder exists, otherwise warn the user
    if not os.path.exists(base_dir):
        print(f"[-] Error: Directory '{base_dir}' not found. Please create it and add your markdown files.")
        return []

    # Find all markdown files inside the knowledge_base folder
    search_path = os.path.join(base_dir, "*.md")
    markdown_files = glob.glob(search_path)
    
    if not markdown_files:
        print(f"[-] Warning: No markdown files found in '{base_dir}'.")
        return []

    print(f"[+] Found {len(markdown_files)} technical documentation files. Processing...")

    all_chunks = []

    # Loop through every markdown file found
    for file_path in markdown_files:
        file_name = os.path.basename(file_path)
        
        # Open and read the text content of the markdown file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[-] Error reading {file_name}: {e}")
            continue

        # Simple semantic chunking strategy: 
        # Technical documentation is naturally split by headers (e.g., '## Error:')
        # We split the file text wherever we encounter '## '
        sections = content.split("\n## ")
        
        for i, section in enumerate(sections):
            # If a section was split, add the '## ' prefix back to make it readable
            if i > 0:
                section_text = "## " + section.strip()
            else:
                section_text = section.strip()

            # Skip empty chunks
            if not section_text:
                continue

            # Create a dictionary (chunk object) containing the text and metadata
            chunk_data = {
                "source_file": file_name,
                "chunk_id": f"{file_name}_chunk_{i}",
                "text": section_text
            }
            
            all_chunks.append(chunk_data)

    print(f"[+] Successfully processed and split files into {len(all_chunks)} total knowledge chunks.")
    return all_chunks

# =============================================================================
# Execution block: Run this script directly to test document loading
# =============================================================================
if __name__ == "__main__":
    print("--- Starting Step 1: Document Ingestion Test ---")
    chunks = load_and_chunk_documents()
    
    # Print out a sample of the first chunk to verify everything works properly
    if chunks:
        print("\n[Example Preview of Chunk #1]:")
        print(f"Source File : {chunks[0]['source_file']}")
        print(f"Chunk ID    : {chunks[0]['chunk_id']}")
        print(f"Content Preview:\n{chunks[0]['text'][:3000]}...\n")
    print("--- Step 1 Completed Successfully ---")