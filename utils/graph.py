# graph.py
# Kaam: Conflict graph + Claim dependency graph

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


def build_dependency_graph_figure(graph_data):
    # Claim Dependency Graph — Plotly visualization
    claims = graph_data.get("claims", [])
    if not claims:
        return None

    fig = go.Figure()

    question_y = 1.0
    claim_y = 0.6
    evidence_y = 0.2

    # Question node
    fig.add_trace(go.Scatter(
        x=[0.5],
        y=[question_y],
        mode="markers+text",
        text=["❓ Question"],
        textposition="middle center",
        marker=dict(size=50, color="#1f77b4", line=dict(width=2, color="#333")),
        name="Question",
        hoverinfo="text",
        hovertext=[graph_data.get("question", "")]
    ))

    n = len(claims)
    for i, claim in enumerate(claims):
        x = (i + 0.5) / n
        confidence = claim.get("confidence", "medium")
        color = {"high": "#28a745", "medium": "#ffc107", "low": "#dc3545"}.get(confidence, "#ffc107")

        fig.add_trace(go.Scatter(
            x=[x],
            y=[claim_y],
            mode="markers+text",
            text=[f"📌 {claim.get('id', 'C')}"],
            textposition="middle center",
            marker=dict(size=40, color=color, line=dict(width=2, color="#333")),
            name=f"Claim {claim.get('id', '')}",
            hoverinfo="text",
            hovertext=[claim.get("claim", "")]
        ))

        fig.add_trace(go.Scatter(
            x=[0.5, x],
            y=[question_y, claim_y],
            mode="lines",
            line=dict(width=2, color="#999"),
            showlegend=False,
            hoverinfo="none"
        ))

        # Supporting evidence
        for j, sup in enumerate(claim.get("supporting", [])[:3]):
            ex = x + (j - 1) * 0.05
            fig.add_trace(go.Scatter(
                x=[ex],
                y=[evidence_y],
                mode="markers+text",
                text=["✓"],
                textposition="middle center",
                marker=dict(size=25, color="#28a745"),
                name="Support",
                hoverinfo="text",
                hovertext=[f"{sup.get('source', '')} p{sup.get('page', '?')}"],
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[x, ex],
                y=[claim_y, evidence_y],
                mode="lines",
                line=dict(width=1, color="#28a745", dash="dot"),
                showlegend=False,
                hoverinfo="none"
            ))

        # Contradicting evidence
        for j, con in enumerate(claim.get("contradicting", [])[:3]):
            ex = x + (j - 1) * 0.05 + 0.02
            fig.add_trace(go.Scatter(
                x=[ex],
                y=[evidence_y],
                mode="markers+text",
                text=["✗"],
                textposition="middle center",
                marker=dict(size=25, color="#dc3545"),
                name="Contradict",
                hoverinfo="text",
                hovertext=[f"{con.get('source', '')} p{con.get('page', '?')}"],
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[x, ex],
                y=[claim_y, evidence_y],
                mode="lines",
                line=dict(width=1, color="#dc3545", dash="dot"),
                showlegend=False,
                hoverinfo="none"
            ))

    fig.update_layout(
        title="🔗 Claim Dependency Graph",
        showlegend=False,
        height=500,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1.2]),
        plot_bgcolor="white",
        hovermode="closest"
    )

    return fig