from neo4j import GraphDatabase

uri="bolt://localhost:7687"

username="neo4j"

password="medical123"   # your password

driver=GraphDatabase.driver(uri,
auth=(username,password))


# Get Diseases and Symptoms

def get_diseases():

    data={}

    with driver.session() as session:

        result=session.run("""

        MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)

        RETURN d.name as disease,
               collect(s.name) as symptoms

        """)

        for r in result:

            data[r["disease"]]={

            "Symptoms":r["symptoms"],

            "Description":"From Neo4j",

            "Treatment":"Consult Doctor"

            }

    return data