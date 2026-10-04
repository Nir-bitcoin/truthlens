# graph.py
# for: Conflict graph banana (Plotly)

import plotly.graph_objects as go
import networkx as nx


def build_conflict_graph(conflict_data):
    # Conflict data se visual graph banata hai
    pairs = conflict_data.get("pairs", [])
    if not pairs:
        return None

    G = nx.Graph()

    for pair in pairs:
        a = pair.get("source_a", "Doc A")
        b = pair.get("source_b", "Doc B")
        G.add_edge(a, b, label="conflict")

    pos = nx.spring_layout(G, seed=42)

    # Edges
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color="#dc3545"),
        hoverinfo="none",
        mode="lines"
    )

    # Nodes
    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        marker=dict(size=30, color="#ffc107", line=dict(width=2, color="#333")),
        hoverinfo="text"
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=400,
            plot_bgcolor="white"
        )
    )

    return fig