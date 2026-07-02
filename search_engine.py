import json
import os
import chromadb
from chromadb.utils import embedding_functions

CATALOG_DICT = {}
CATALOG_LIST = []
CATALOG_BY_URL = {}
CHROMA_CLIENT = None
CHROMA_COLLECTION = None

def normalize_url(url: str) -> str:
    url = url.strip().lower()
    if url.endswith("/"):
        url = url[:-1]
    return url

def clean_json_string(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    out = []
    in_string = False
    escape = False
    for char in content:
        if char == '\"' and not escape:
            in_string = not in_string
            out.append(char)
        elif char == '\\\\' and in_string:
            escape = not escape
            out.append(char)
        else:
            if escape:
                escape = False
            if in_string and (char == '\n' or char == '\r'):
                out.append(' ')
            else:
                out.append(char)
    return ''.join(out)

def load_and_clean_data():
    global CATALOG_DICT, CATALOG_LIST, CATALOG_BY_URL, CHROMA_CLIENT, CHROMA_COLLECTION

    filepath = "catalog.json"
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} file not found.")
        return

    # Clean and parse the raw JSON (handles newlines inside strings)
    cleaned_str = clean_json_string(filepath)
    raw_data = json.loads(cleaned_str)

    cleaned_catalog = []

    # Clean leading/trailing spaces in keys and values
    for item in raw_data:
        cleaned_item = {}
        for key, val in item.items():
            clean_key = key.strip()

            if isinstance(val, str):
                clean_val = val.strip()
            elif isinstance(val, list):
                clean_val = []
                for element in val:
                    if isinstance(element, str):
                        clean_val.append(element.strip())
                    else:
                        clean_val.append(element)
            else:
                clean_val = val

            cleaned_item[clean_key] = clean_val

        cleaned_catalog.append(cleaned_item)

    CATALOG_DICT = {}
    CATALOG_LIST = []
    CATALOG_BY_URL = {}

    for item in cleaned_catalog:
        entity_id = item.get("entity_id")
        if not entity_id:
            continue

        CATALOG_DICT[str(entity_id)] = item
        CATALOG_LIST.append(item)
        
        link = item.get("link")
        if link:
            CATALOG_BY_URL[normalize_url(link)] = item

    # Initialize Chroma client (in-memory EphemeralClient)
    CHROMA_CLIENT = chromadb.EphemeralClient()
    emb_func = embedding_functions.DefaultEmbeddingFunction()
    
    # Recreate the collection to ensure no duplicate additions on startup re-runs
    try:
        CHROMA_CLIENT.delete_collection("shl_catalog")
    except Exception:
        pass
        
    CHROMA_COLLECTION = CHROMA_CLIENT.create_collection("shl_catalog", embedding_function=emb_func)

    ids = []
    documents = []
    metadatas = []

    for item in CATALOG_LIST:
        entity_id = str(item.get("entity_id", "")).strip()
        name = item.get("name", "")
        description = item.get("description", "")
        keys = item.get("keys", [])
        keys_str = ", ".join(keys)
        text_blob = f"{name}. {description}. Keys: {keys_str}"

        ids.append(entity_id)
        documents.append(text_blob)
        metadatas.append({
            "name": name,
            "link": item.get("link", ""),
            "keys_str": keys_str
        })

    if documents:
        CHROMA_COLLECTION.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Chroma DB collection built: {len(CATALOG_LIST)} assessments indexed.")
    else:
        print("Warning: no catalog items to index in Chroma DB.")

def search(query: str, top_k: int = 25):
    global CHROMA_COLLECTION, CATALOG_DICT

    if CHROMA_COLLECTION is None:
        return []

    # Query Chroma DB
    results = CHROMA_COLLECTION.query(
        query_texts=[query],
        n_results=top_k
    )

    if not results or not results["ids"] or len(results["ids"][0]) == 0:
        return []

    hits = []
    for id_ in results["ids"][0]:
        str_id = str(id_).strip()
        if str_id in CATALOG_DICT:
            item = CATALOG_DICT[str_id]
            hits.append({
                "entity_id": item.get("entity_id", ""),
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "keys": item.get("keys", [])
            })
    return hits
