from langchain_core.tools import tool
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, ScoredPoint
@tool
def search_knowledge(query: str):
    """Tool to extract the cases of restoring ruined objects and their price of repairment.
        This tool is used to get approximate understanding how much money would repairment cost 
        comparing to real cases"""

    client = QdrantClient(host="localhost", port=6333)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    query_text = query

    query_embedding = model.encode(query_text).tolist()

    collection_name = "parsed_data_collection"

    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=5,  
        score_threshold=0.5,  
        with_payload=True
    )
    result = [result.payload for result in search_result]

    return result