import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os

def show_network(category="All"):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "cleaned_dataset.csv")
    data = pd.read_csv(csv_path)

    # Mapping diseases to specific categories to "divide" the graph
    medical_map = {
        "Respiratory": ["Pneumonia", "Tuberculosis", "Bronchial Asthma", "Common Cold"],
        "Digestive": ["GERD", "Peptic ulcer diseae", "Gastroenteritis", "Jaundice"],
        "Skin": ["Fungal infection", "Acne", "Psoriasis", "Impetigo"],
        "Infectious": ["Malaria", "Dengue", "Typhoid", "Chicken pox"],
        "Chronic": ["Diabetes", "Hypertension", "Hyperthyroidism", "Arthritis"]
    }

    # Filter data based on selection
    if category in medical_map:
        target_diseases = medical_map[category]
        # Only take unique combinations to keep lines clean
        df = data[data["Disease"].isin(target_diseases)].drop_duplicates()
    else:
        # For 'All', only show the first 5 diseases so it doesn't get clumsy
        df = data.drop_duplicates().head(5)

    G = nx.Graph()
    symptoms_cols = list(df.columns[:-1])

    for i in range(len(df)):
        disease = df.iloc[i]["Disease"]
        G.add_node(disease, node_type='disease')
        for s in symptoms_cols:
            if df.iloc[i][s] == 1:
                G.add_node(s, node_type='symptom')
                G.add_edge(disease, s)

    # --- THE LAYOUT TRICK ---
    plt.figure(figsize=(15, 12))

    # k=5.0 is a massive force that pushes symptoms away from the center
    pos = nx.spring_layout(G, k=5.0, iterations=100)

    # Separate for styling
    d_nodes = [n for n, a in G.nodes(data=True) if a.get('node_type') == 'disease']
    s_nodes = [n for n, a in G.nodes(data=True) if a.get('node_type') == 'symptom']

    # Draw nodes: Diseases are large circles, Symptoms are smaller
    nx.draw_networkx_nodes(G, pos, nodelist=d_nodes, node_color='#FF4B2B', node_size=3000, alpha=0.9)
    nx.draw_networkx_nodes(G, pos, nodelist=s_nodes, node_color='#2BC0E4', node_size=1000, alpha=0.4)

    # Draw Edges: Thin and light
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.2, edge_color='gray')

    # Draw Labels: Inside a nice box so they don't overlap
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold',
                           bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0.5))

    plt.title(f"Diagnostic Mapping: {category} Systems", fontsize=18, pad=20)
    plt.axis('off')

    save_path = os.path.join(BASE_DIR, "static", f"network_{category}.png")
    plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.close()