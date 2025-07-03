import os
import re
from dotenv import load_dotenv

from pinecone import Pinecone
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.vector_stores.pinecone import PineconeVectorStore
from together import Together

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX_NAME", "civbotvect")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_MODEL   = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")

SYSTEM_PROMPT = (
    "Вы — опытный помощник, специализирующийся на механике Civilization VI. "
    "Для ответа используйте только предоставленную контекстную информацию"
    "и историю разговоров, а также говорите только по-русски, по возможности"
    "старайся обращаться к пользователю по имени."
)

embed_model = HuggingFaceEmbedding(model_name="cointegrated/rubert-tiny2")
splitter = SemanticSplitterNodeParser(
    buffer_size=2,
    breakpoint_percentile_threshold=60,
    embed_model=embed_model,
)

Settings.embed_model = embed_model
Settings.node_parser = splitter
Settings.llm = None  

together = Together(api_key=TOGETHER_API_KEY)

class RAGService:
    def __init__(self):
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        pc_index = pinecone_client.Index(PINECONE_INDEX)
        store = PineconeVectorStore(pinecone_index=pc_index)
        storage_context = StorageContext.from_defaults(vector_store=store)
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=store,
            storage_context=storage_context,
        )
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            hybrid=True,            
            alpha=0.4,              
            streaming=False,
            response_mode="compact",
        )

    async def retrieve_and_generate(self, user_input: str, history: list) -> str:
        result = self.query_engine.query(user_input)
        hits = result.source_nodes 

        fragments = []
        for node in hits:
            text = node.node.get_content() if hasattr(node.node, "get_content") else str(node.node.text)

            lines = [ln.strip() for ln in text.splitlines()
                if ln.strip() and not ln.strip().startswith("file_path:")]

            for ln in lines:
                if ln not in fragments:
                    fragments.append(ln)

        context = "\n".join(fragments)[:4000]

        rerank_prompt = "From the following context fragments, choose the 2 most relevant to the query:\n\n"
        for i, frag in enumerate(fragments, 1):
            rerank_prompt += f"{i}. {frag}\n"
        rerank_prompt += f"\nQuery: {user_input}\nAnswer:"

        rerank_resp = together.chat.completions.create(
            model=TOGETHER_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": rerank_prompt},
            ],
            stream=False,
        )
        sel = rerank_resp.choices[0].message.content
        selected_idxs = [int(x) for x in re.findall(r"\b\d+\b", sel)[:2]]
        best_context = "\n".join(fragments[i-1] for i in selected_idxs if 1 <= i <= len(fragments))

        if history:
            hist_lines = []
            for m in history:
                role = "User" if m.type == "user" else "Assistant"
                hist_lines.append(f"{role}: {m.text}")
            history_text = "\n".join(hist_lines)
        else:
            history_text = ""

        final_prompt = (
            "=== Context ===\n"
            f"{best_context}\n\n"
            "=== History ===\n"
            f"{history_text}\n\n"
            "=== Query ===\n"
            f"{user_input}\n\n"
            "=== Assistant Answer ===\n"
        )
        print(final_prompt)
        resp = together.chat.completions.create(
            model=TOGETHER_MODEL,
            messages=[
                {"role": "system",  "content": SYSTEM_PROMPT},
                {"role": "user",    "content": final_prompt},
            ],
            stream=False,
        )
        return resp.choices[0].message.content
