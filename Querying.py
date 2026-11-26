from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# -----------------------------
# Load .env file
# -----------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

# -----------------------------
# Load Neo4j credentials
# -----------------------------
def load_credentials(file_path="credentials.txt"):
    creds = {}
    with open(file_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key] = value
    return creds

creds = load_credentials()

NEO4J_URI = creds["NEO4J_URI"]
NEO4J_USERNAME = creds["NEO4J_USERNAME"]
NEO4J_PASSWORD = creds["NEO4J_PASSWORD"]
NEO4J_DATABASE = creds["NEO4J_DATABASE"]

# -----------------------------
# Initialize Neo4j graph
# -----------------------------
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE
)

# -----------------------------
# Initialize LLM
# -----------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

# -----------------------------
# Build QA chain
# -----------------------------
qa_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True
)

# -----------------------------
# Test query
# -----------------------------
response = qa_chain.invoke("List all Entity nodes.")
print(response)
