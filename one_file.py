import pulp
import matplotlib.pyplot as plt
import tkinter as tk
import networkx as nx
from typing import Dict, List, Tuple
import folium

military_warehouses: List[str] = ['Warehouse1', 'Warehouse2', 'Warehouse3', 'Warehouse4', 'Warehouse5']
retailers: List[str] = [
    'Mykolaiv', 'Kherson', 'Kharkiv', 'Zaporizhzhia',
    'Kramatorsk', 'Pavlohrad', 'Izyum', 'Dnipro'
]

supply: Dict[str, int] = {
    'Warehouse1': 100,
    'Warehouse2': 150,
    'Warehouse3': 200,
    'Warehouse4': 250,
    'Warehouse5': 300
}

demand: Dict[str, int] = {
    'Mykolaiv': 80,
    'Kherson': 70,
    'Kharkiv': 90,
    'Zaporizhzhia': 110,
    'Kramatorsk': 120,
    'Pavlohrad': 100,
    'Izyum': 140,
    'Dnipro': 130
}

costs: Dict[Tuple[str, str], int] = {
    ('Warehouse1', 'Mykolaiv'): 2,
    ('Warehouse1', 'Kherson'): 3,
    ('Warehouse1', 'Kharkiv'): 1,
    ('Warehouse1', 'Zaporizhzhia'): 4,
    ('Warehouse1', 'Kramatorsk'): 5,
    ('Warehouse1', 'Pavlohrad'): 6,
    ('Warehouse1', 'Izyum'): 7,
    ('Warehouse1', 'Dnipro'): 8,
    ('Warehouse2', 'Mykolaiv'): 3,
    ('Warehouse2', 'Kherson'): 1,
    ('Warehouse2', 'Kharkiv'): 2,
    ('Warehouse2', 'Zaporizhzhia'): 5,
    ('Warehouse2', 'Kramatorsk'): 4,
    ('Warehouse2', 'Pavlohrad'): 3,
    ('Warehouse2', 'Izyum'): 6,
    ('Warehouse2', 'Dnipro'): 4,
    ('Warehouse3', 'Mykolaiv'): 4,
    ('Warehouse3', 'Kherson'): 2,
    ('Warehouse3', 'Kharkiv'): 3,
    ('Warehouse3', 'Zaporizhzhia'): 1,
    ('Warehouse3', 'Kramatorsk'): 5,
    ('Warehouse3', 'Pavlohrad'): 4,
    ('Warehouse3', 'Izyum'): 2,
    ('Warehouse3', 'Dnipro'): 3,
    ('Warehouse4', 'Mykolaiv'): 3,
    ('Warehouse4', 'Kherson'): 4,
    ('Warehouse4', 'Kharkiv'): 5,
    ('Warehouse4', 'Zaporizhzhia'): 2,
    ('Warehouse4', 'Kramatorsk'): 1,
    ('Warehouse4', 'Pavlohrad'): 3,
    ('Warehouse4', 'Izyum'): 4,
    ('Warehouse4', 'Dnipro'): 5,
    ('Warehouse5', 'Mykolaiv'): 6,
    ('Warehouse5', 'Kherson'): 5,
    ('Warehouse5', 'Kharkiv'): 4,
    ('Warehouse5', 'Zaporizhzhia'): 3,
    ('Warehouse5', 'Kramatorsk'): 2,
    ('Warehouse5', 'Pavlohrad'): 6,
    ('Warehouse5', 'Izyum'): 7,
    ('Warehouse5', 'Dnipro'): 8
}

data = {
    'Name': [
        'Warehouse1', 'Warehouse2', 'Warehouse3', 'Warehouse4', 'Warehouse5',
        'Mykolaiv', 'Kherson', 'Kharkiv',
        'Zaporizhzhia', 'Kramatorsk', 'Pavlohrad', 'Izyum', 'Dnipro'
    ],
    'Latitude': [
        47.1, 46.8, 48.5, 48.9, 48.6,  # Coordinates for Warehouses (can be adjusted)
        46.9659, 46.6354, 50.0048, 47.8388, 48.7200, 48.5351, 49.2085, 48.4647  # Accurate coords for cities
    ],
    'Longitude': [
        32.0, 32.4, 35.5, 35.8, 37.1,  # Coordinates for Warehouses (can be adjusted)
        32.0026, 32.6178, 36.2319, 35.1396, 37.5556, 35.8690, 37.2484, 35.0462  # Accurate coords for cities
    ]
}


def create_model() -> pulp.LpProblem:
    model = pulp.LpProblem("Supply_Chain_Optimization", pulp.LpMinimize)

    shipping_vars = pulp.LpVariable.dicts("Shipping", (military_warehouses, retailers), lowBound=0, cat='Continuous')

    model += pulp.lpSum(
        costs[w, r] * shipping_vars[w][r] for w in military_warehouses for r in retailers), "Total_Transportation_Cost"

    for w in military_warehouses:
        model += pulp.lpSum(shipping_vars[w][r] for r in retailers) <= supply[w], f"Supply_Constraint_{w}"

    for r in retailers:
        model += pulp.lpSum(shipping_vars[w][r] for w in military_warehouses) >= demand[r], f"Demand_Constraint_{r}"

    return model, shipping_vars


def solve_model(model: pulp.LpProblem):
    model.solve()


def display_results(model: pulp.LpProblem, shipping_vars: Dict[str, Dict[str, pulp.LpVariable]]):
    root = tk.Tk()
    root.title("Transportation Problem Results")

    output_text = tk.Text(root, wrap=tk.WORD, width=50, height=20)
    output_text.pack(pady=10)

    output_text.insert(tk.END, f"Status: {pulp.LpStatus[model.status]}\n")

    for w in military_warehouses:
        for r in retailers:
            if shipping_vars[w][r].varValue > 0:
                output_text.insert(tk.END, f"Ship {shipping_vars[w][r].varValue} units from {w} to {r}\n")

    output_text.insert(tk.END, f"Total Transportation Cost: {pulp.value(model.objective)}\n")

    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=10)

    root.mainloop()


def visualize_shipping(shipping_vars: Dict[str, Dict[str, pulp.LpVariable]]):
    shipping_data = {}
    for w in military_warehouses:
        shipping_data[w] = []
        for r in retailers:
            if shipping_vars[w][r].varValue > 0:
                shipping_data[w].append(shipping_vars[w][r].varValue)
            else:
                shipping_data[w].append(0)

    num_warehouses = len(military_warehouses)
    fig, axes = plt.subplots(1, num_warehouses, figsize=(5 * num_warehouses, 5))

    for i, w in enumerate(military_warehouses):
        shipments = shipping_data[w]
        retailers_with_shipments = [r for r, s in zip(retailers, shipments) if s > 0]
        shipment_values = [s for s in shipments if s > 0]

        axes[i].pie(shipment_values, labels=retailers_with_shipments, autopct='%1.1f%%', startangle=90)
        axes[i].set_title(f'Units Shipped from {w}')
        axes[i].axis('equal')  # Ensures pie is a circle

    plt.tight_layout()
    plt.show()


def visualize_network(shipping_vars: Dict[str, Dict[str, pulp.LpVariable]]):
    G = nx.DiGraph()

    for w in military_warehouses:
        G.add_node(w, type='warehouse')
    for r in retailers:
        G.add_node(r, type='retailer')

    for w in military_warehouses:
        for r in retailers:
            if shipping_vars[w][r].varValue > 0:
                G.add_edge(w, r, weight=shipping_vars[w][r].varValue)

    pos = nx.spring_layout(G)

    nx.draw(G, pos, with_labels=True,
            node_color=['skyblue' if G.nodes[n]['type'] == 'warehouse' else 'lightgreen' for n in G.nodes],
            node_size=2000, font_size=10, font_weight='bold', arrows=True)

    # Add edge labels
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Transportation Network")
    plt.show()


def create_map(shipping_vars: Dict[str, Dict[str, pulp.LpVariable]]):
    map_center = [48.5, 35.5]  # Approximate center of the area
    folium_map = folium.Map(location=map_center, zoom_start=6)

    for warehouse in military_warehouses:
        folium.Marker(
            location=[data['Latitude'][military_warehouses.index(warehouse)], data['Longitude'][military_warehouses.index(warehouse)]],
            popup=warehouse,
            icon=folium.Icon(color='blue')
        ).add_to(folium_map)

    for r in retailers:
        folium.Marker(
            location=[data['Latitude'][len(military_warehouses) + retailers.index(r)],
                      data['Longitude'][len(military_warehouses) + retailers.index(r)]],
            popup=r,
            icon=folium.Icon(color='green')
        ).add_to(folium_map)

        for w in military_warehouses:
            if shipping_vars[w][r].varValue > 0:
                folium.PolyLine(
                    locations=[
                        [data['Latitude'][military_warehouses.index(w)], data['Longitude'][military_warehouses.index(w)]],
                        [data['Latitude'][len(military_warehouses) + retailers.index(r)],
                         data['Longitude'][len(military_warehouses) + retailers.index(r)]]
                    ],
                    color='blue',
                    weight=2.5,
                    opacity=0.7
                ).add_to(folium_map)

                mid_lat = (data['Latitude'][military_warehouses.index(w)] + data['Latitude'][
                    len(military_warehouses) + retailers.index(r)]) / 2
                mid_lng = (data['Longitude'][military_warehouses.index(w)] + data['Longitude'][
                    len(military_warehouses) + retailers.index(r)]) / 2
                folium.Marker(
                    location=[mid_lat, mid_lng],
                    popup=f"Cost: {costs[(w, r)]}",
                    icon=folium.DivIcon(html=f"<div style='font-size: 12px; color: black;'>{costs[(w, r)]}</div>")
                ).add_to(folium_map)

    folium_map.save('transportation_map_with_costs.html')
    print("Map saved as 'transportation_map_with_costs.html'.")


def main():
    model, shipping_vars = create_model()
    solve_model(model)
    display_results(model, shipping_vars)
    visualize_shipping(shipping_vars)
    visualize_network(shipping_vars)
    create_map(shipping_vars)


if __name__ == "__main__":
    main()
