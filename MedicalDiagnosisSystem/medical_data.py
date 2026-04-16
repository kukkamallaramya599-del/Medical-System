from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "medical123"

driver = GraphDatabase.driver(uri, auth=(username, password))

def create_data():

    with driver.session() as session:

        # Create Diseases
        session.run("CREATE (:Disease {name:'Flu'})")
        session.run("CREATE (:Disease {name:'Malaria'})")
        session.run("CREATE (:Disease {name:'Dengue'})")

        # Create Symptoms
        session.run("CREATE (:Symptom {name:'Fever'})")
        session.run("CREATE (:Symptom {name:'Cough'})")
        session.run("CREATE (:Symptom {name:'Headache'})")

        # Create Relationships
        session.run("""
        MATCH (s:Symptom {name:'Fever'}),(d:Disease {name:'Malaria'})
        CREATE (s)-[:INDICATES]->(d)
        """)

        session.run("""
        MATCH (s:Symptom {name:'Cough'}),(d:Disease {name:'Flu'})
        CREATE (s)-[:INDICATES]->(d)
        """)

        session.run("""
        MATCH (s:Symptom {name:'Headache'}),(d:Disease {name:'Dengue'})
        CREATE (s)-[:INDICATES]->(d)
        """)

        print("Medical Data Created")

create_data()
driver.close()