from glob import glob
from app.core.llm import openai_client
from pymilvus import MilvusClient
from tqdm import tqdm
import json
from pypdf import PdfReader 

milvus_client = MilvusClient(uri="/home/ubuntu/engrammer-api/data/milvus.db")

collection_name="knowledge_base_collection"

def emb_text(text):
    return (
        openai_client.embeddings.create(input=text, model="text-embedding-3-small")
        .data[0]
        .embedding
    )
    
def seed():
    
    text_lines = []

    for file_path in glob("/home/ubuntu/engrammer-api/app/docs/guerras_cantabras/*.pdf", recursive=True):
        reader = PdfReader(file_path)
        file_text = ""
        for page in reader.pages:
            file_text += page.extract_text() or "" 
        text_lines += file_text.split("\n\n")
    
    if milvus_client.has_collection(collection_name):
        milvus_client.drop_collection(collection_name)
        
    milvus_client.create_collection(
        collection_name=collection_name,
        dimension=1536,
        metric_type="IP",  
        consistency_level="Bounded"
    )
    
    data = []

    for i, line in enumerate(tqdm(text_lines, desc="Creating embeddings")):
        data.append({"id": i, "vector": emb_text(line), "text": line})

    milvus_client.insert(collection_name=collection_name, data=data)
        
def test():
    
    question = "How is data stored in milvus?"
    
    search_res = milvus_client.search(
        collection_name= collection_name,
        data=[
            emb_text(question)
        ],  # Use the `emb_text` function to convert the question to an embedding vector
        limit=3,  # Return top 3 results
        search_params={"metric_type": "IP", "params": {}},  # Inner product distance
        output_fields=["text"],  # Return the text field
    )
    
    retrieved_lines_with_distances = [
        (res["entity"]["text"], res["distance"]) for res in search_res[0]
    ]
    # print(json.dumps(retrieved_lines_with_distances, indent=4))
    
    context = "\n".join(
        [line_with_distance[0] for line_with_distance in retrieved_lines_with_distances]
    )
    
    print("Context for the question:")
    print(context)

       
def main():
        
    print("Seeding Milvus with data...")
    seed()
    # test()
    

    
if __name__ == "__main__":
    main()