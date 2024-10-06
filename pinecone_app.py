# RESEARCH ON QUESTIONS  ##################################################################################################################
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import AzureOpenAIEmbeddings
import time


azure_configs = {

}




pc = Pinecone(api_key=your_api_key)
index_name = your_pc_index


# pc.create_index(
#     name=index_name,
#     dimension=1024,
#     metric="cosine",
#     spec=ServerlessSpec(
#         cloud="aws",
#         region="us-east-1"
#     ) 
# )

# Wait for the index to be ready
while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)


azure_embeddings = AzureOpenAIEmbeddings(
    openai_api_version="2023-05-15",
    azure_endpoint=azure_configs["base_url"],
    azure_deployment=azure_configs["embedding_deployment"],
    model=azure_configs["embedding_name"],
)

df = pd.read_json("hf://datasets/HuggingFaceH4/instruction-dataset/step3-eval.jsonl", lines=True)

li_questions = [df["prompt"][k] for k in range(len(df["prompt"]))]
li_answers = [df["completion"][k] for k in range(len(df["completion"]))]
embeddings = azure_embeddings.embed_documents(li_questions)

index = pc.Index(index_name)
vectors = []
assert len(embeddings) == len(li_questions)
for k in range(len(embeddings)):
    vectors.append({
        "id": str(k),
        "values": embeddings[k],
        "metadata": {'question': li_questions[k], 'answer': li_answers[k]}
    })

index.upsert(
    vectors=vectors,
    namespace="ns1"
)


# query = "Tell me about the tech company known as Apple."

# embedding = pc.inference.embed(
#     model="multilingual-e5-large",
#     inputs=[query],
#     parameters={
#         "input_type": "query"
#     }
# )

# results = index.query(
#     namespace="ns1",
#     vector=embedding[0].values,
#     top_k=3,
#     include_values=False,
#     include_metadata=True
# )

# print(results)

