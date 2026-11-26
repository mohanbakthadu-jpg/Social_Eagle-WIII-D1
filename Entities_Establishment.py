import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from Doc_Loader import load_and_split_pdf


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env", override=True)

NER_PROMPT = ChatPromptTemplate.from_template("""
You are an expert NER system. Extract all named entities from the text.

Return ONLY valid JSON in this format:
{{
  "entities": [
    {{"name": "...", "type": "..."}}
  ]
}}

Entity types allowed: PERSON, ORG, LOCATION, DATE, EVENT, PRODUCT, WORK_OF_ART, LAW, LANGUAGE, OTHER.

Text:
{chunk}
""")


def extract_entities(chunks):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    ner_chain = NER_PROMPT | llm | StrOutputParser()
    all_entities = []
    total = len(chunks)

    for index, chunk in enumerate(chunks, start=1):
        print(f"Processing chunk {index}/{total}...", flush=True)
        response = ner_chain.invoke({"chunk": chunk.page_content})
        try:
            data = json.loads(response)
            all_entities.extend(data.get("entities", []))
        except (json.JSONDecodeError, TypeError) as error:
            print(f"JSON parsing error in chunk {index}: {error}", flush=True)

    return all_entities


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY was not found. Add it to a .env file next to "
            "Entities_Establishment.py as: OPENAI_API_KEY=your_api_key"
        )

    print("Loading PDF...", flush=True)
    chunks = load_and_split_pdf(PROJECT_DIR / "sample.pdf")
    print(f"Loaded {len(chunks)} text chunks.", flush=True)
    if not chunks:
        raise SystemExit("The PDF did not contain extractable text.")

    entities = extract_entities(chunks)
    print(f"Total entities extracted: {len(entities)}")
    for entity in entities[:10]:
        print(entity)
