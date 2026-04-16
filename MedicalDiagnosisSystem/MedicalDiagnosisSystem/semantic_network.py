import networkx as nx
import matplotlib.pyplot as plt

def show_network():

    G = nx.Graph()

    data = {

    "Flu": {
        "Symptoms": ["Fever","Cough","Headache"],
        "Doctor": "General Physician"
    },

    "Dengue": {
        "Symptoms": ["Fever","Chills","Body Pain"],
        "Doctor": "General Physician"
    }

    }

    for disease in data:

        G.add_node(disease)

        for s in data[disease]["Symptoms"]:
            G.add_node(s)
            G.add_edge(disease, s)

        doctor = data[disease]["Doctor"]
        G.add_node(doctor)
        G.add_edge(disease, doctor)


    plt.figure(figsize=(8,6))

    nx.draw(G,
            with_labels=True,
            node_color='lightblue',
            node_size=2000,
            font_size=10)

    plt.title("Medical Semantic Network")

    # SAVE IMAGE instead of show
    plt.savefig("static/network.png")

    plt.close()