import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from Doc_Loader import load_and_split_pdf
from Entities_Establishment import extract_entities


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env", override=True)

RELATION_PROMPT = ChatPromptTemplate.from_template("""
You are an expert relationship extraction system.

Given the text and the list of entities, extract all meaningful relationships.

Return ONLY valid JSON in this format:
{{
  "triples": [
    {{"subject": "...", "relation": "...", "object": "..."}}
  ]
}}

Rules:
- Use only entities provided.
- Relations must be verbs or meaningful phrases (e.g., WORKS_FOR, LOCATED_IN, FOUNDED, BORN_IN).
- Do NOT hallucinate entities.
- If no relationships exist, return {{"triples": []}}.

Entities:
{entities}

Text:
{chunk}
""")


def extract_relationships(chunks, entities):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    relation_chain = RELATION_PROMPT | llm | StrOutputParser()
    all_triples = []

    for index, chunk in enumerate(chunks, start=1):
        print(f"Mapping relationships for chunk {index}/{len(chunks)}...", flush=True)
        response = relation_chain.invoke({
            "chunk": chunk.page_content,
            "entities": json.dumps(entities),
        })
        try:
            data = json.loads(response)
            all_triples.extend(data.get("triples", []))
        except (json.JSONDecodeError, TypeError) as error:
            print(f"JSON parsing error in chunk {index}: {error}", flush=True)

    return all_triples


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY was not found. Add it to a .env file next to "
            "Relationship_Mapping.py as: OPENAI_API_KEY=your_api_key"
        )

    chunks = load_and_split_pdf(PROJECT_DIR / "sample.pdf")
    if not chunks:
        raise SystemExit("The PDF did not contain extractable text.")

    print("Extracting entities...", flush=True)
    entities = extract_entities(chunks)
    print(f"Extracted {len(entities)} entities.", flush=True)

    triples = extract_relationships(chunks, entities)
    print(f"Total triples extracted: {len(triples)}")
    for triple in triples[:10]:
        print(triple)
