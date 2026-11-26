from neo4j import GraphDatabase

# -----------------------------
# Load credentials from text file
# -----------------------------
def load_credentials(file_path="credentials.txt"):
    creds = {}
    with open(file_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key] = value
    return creds

# -----------------------------
# Load values BEFORE using them
# -----------------------------
creds = load_credentials()

NEO4J_URI = creds["NEO4J_URI"]              # neo4j+ssc://aa339f0f.databases.neo4j.io
NEO4J_USERNAME = creds["NEO4J_USERNAME"]    # aa339f0f
NEO4J_PASSWORD = creds["NEO4J_PASSWORD"]    # your Aura password
NEO4J_DATABASE = creds["NEO4J_DATABASE"]    # MUST be aa339f0f for Aura Free

# -----------------------------
# Create driver (Aura-safe)
# -----------------------------
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

# -----------------------------
# Create constraint
# -----------------------------
CREATE_CONSTRAINT_QUERY = """
CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
FOR (e:Entity)
REQUIRE e.name IS UNIQUE
"""

with driver.session(database=NEO4J_DATABASE) as session:
    session.run(CREATE_CONSTRAINT_QUERY)

# -----------------------------
# Ingest functions
# -----------------------------
def ingest_triple(session, subject, relation, object_):
    cypher = f"""
    MERGE (s:Entity {{name: $subject}})
    MERGE (o:Entity {{name: $object}})
    MERGE (s)-[r:{relation}]->(o)
    """
    session.run(cypher, subject=subject, object=object_)

def build_knowledge_graph(triples):
    with driver.session(database=NEO4J_DATABASE) as session:
        session.run(CREATE_CONSTRAINT_QUERY)
        for t in triples:
            subject = t["subject"]
            relation = t["relation"].upper().replace(" ", "_")
            object_ = t["object"]
            ingest_triple(session, subject, relation, object_)

with driver.session(database=NEO4J_DATABASE) as session:
    print(session.run("RETURN 1 AS test").single()["test"])