from neo4j import GraphDatabase

# Connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "medical123"

driver = GraphDatabase.driver(uri, auth=(username, password))

def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Neo4j Connected Successfully' AS message")
        for record in result:
            print(record["message"])

test_connection()
driver.close()