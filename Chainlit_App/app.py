import chainlit as cl
import requests
import os
import asyncio
from openai import AsyncAzureOpenAI
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import AzureOpenAIEmbeddings
import time


client = AsyncAzureOpenAI(api_key=your_api_key, ...)

azure_configs = {

}

azure_embeddings = AzureOpenAIEmbeddings(
    openai_api_version="2023-05-15",
    azure_endpoint=azure_configs["base_url"],
    azure_deployment=azure_configs["embedding_deployment"],
    model=azure_configs["embedding_name"],
)


pc = Pinecone(api_key=api_pinecone)
index_name = "index_name"
index = pc.Index(index_name)


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Why is the sky blue?",
            message="Explain to me why is the sky blue?",
            icon="/public/idea.svg",
            ),
        cl.Starter(
            label="The religion of Jesus Christ?",
            message="What was the religion of Jesus Christ?",
            icon="/public/learn.svg",
            ),
        cl.Starter(
            label="Cybersecurity Ransomware",
            message="My company has been attacked by a RansomWare, what should I do?",
            icon="/public/terminal.svg",
            ),
        ]


@cl.on_message
async def main(message: cl.Message):
    query = message.content

    query_embedding = azure_embeddings.embed_query(query)

    results = index.query(
        namespace="ns1",
        vector=query_embedding,
        top_k=3,
        include_values=False,
        include_metadata=True
    )

    # Vérifiez si des résultats ont été retournés
    if results.matches:
        string_source = ""
        for result in results.matches:
            string_source += "- " + result["metadata"]["question"] + "\n"

        msg = cl.Message(
            content="",
            elements=[
                cl.Text(
                    name="Most Similar Questions",
                    content=string_source,
                    display="inline"
                )
            ]
        )
        await msg.send()

        response = results.matches[0]["metadata"]["answer"]
        await cl.Message(response).send()
    else:
        await cl.Message("Aucun résultat trouvé.").send()

@cl.on_chat_end
def end():
    print("goodbye", cl.user_session.get("id")) 


