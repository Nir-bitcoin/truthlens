"""
TruthLens — Independence Engine

Yeh module check karta hai ki evidence sources kitne independent hain.

Problem:
    12 sources dikh sakte hain, lekin agar sab same press release
    copy kar rahe hain, toh woh actually 1 independent source hai.

Solution:
    1. Sources ko clusters mein group karo (domain + title similarity)
    2. Independent clusters count karo
    3. "Yeh source hata toh verdict kya?" simulate karo

Important Rules:
    - Source count != Independent evidence count
    - Same domain = same cluster
    - Similar title = same cluster
    - Union-Find algorithm use karte hain
"""

import re
from typing import Any, Dict, List
from urllib.parse import urlparse
from collections import defaultdict


# ============================================================
# CONFIG
# ============================================================

TITLE_SIMILARITY_THRESHOLD = 0.50   # 0.50 = 50% Jaccard overlap
SAME_DOMAIN_CLUSTERS = True          # Same domain = same cluster


# ============================================================
# MAIN FUNCTION 1: Cluster Sources
# ============================================================

def cluster_sources(sources: List[Any]) -> Dict[str, Any]:
    """
    Evidence sources ko clusters mein group karta hai.

    Input:
        sources: list of evidence items (dict ya Document object)

    Output:
        {
            "clusters": [
                {
                    "cluster_id": "cluster_1",
                    "size": 7,
                    "domain": "reuters.com",
                    "source_indices": [0, 2, 3, 5, 7, 8, 9],
                    "representative_title": "...",
                },
                ...
            ],
            "total_sources": 12,
            "independent_clusters": 3,
            "concentration_level": "HIGH"
        }
    """
    if not sources:
        return _empty_cluster_result()

    # Saare sources normalize karo
    normalized = [_normalize_source(s, i) for i, s in enumerate(sources)]

    # Union-Find data structure for clustering
    parent = list(range(len(normalized)))

    def find(x):
        # Path compression
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        # Union by root
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Har pair compare karo
    for i in range(len(normalized)):
        for j in range(i + 1, len(normalized)):
            if _should_cluster(normalized[i], normalized[j]):
                union(i, j)

    # Build clusters from union-find groups
    cluster_map = defaultdict(list)
    for i, item in enumerate(normalized):
        root = find(i)
        cluster_map[root].append(i)

    # Cluster objects banao
    clusters = []
    for cid, indices in cluster_map.items():
        rep = normalized[indices[0]]  # First item = representative
        clusters.append({
            "cluster_id": f"cluster_{cid}",
            "size": len(indices),
            "domain": rep.get("domain", ""),
            "source_indices": indices,
            "representative_title": rep.get("title", "")[:100],
        })

    # Sort: largest cluster first
    clusters.sort(key=lambda c: c["size"], reverse=True)

    total_sources = len(normalized)
    independent_clusters = len(clusters)

    # Concentration level calculate karo
    concentration = _compute_concentration(total_sources, independent_clusters)

    return {
        "clusters": clusters,
        "total_sources": total_sources,
        "independent_clusters": independent_clusters,
        "concentration_level": concentration,
    }


# ============================================================
# MAIN FUNCTION 2: Independence Calculate Karo
# ============================================================

def calculate_independence(cluster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cluster data se independence score nikalo.

    Input:  cluster_sources() ka output
    Output: {
        "score": 0.0 - 1.0,
        "total_sources": int,
        "independent_clusters": int,
        "concentration_level": str,
        "summary": str
    }
    """
    total = cluster_data.get("total_sources", 0)
    independent = cluster_data.get("independent_clusters", 0)
    concentration = cluster_data.get("concentration_level", "UNKNOWN")

    if total == 0:
        return {
            "score": 0.0,
            "total_sources": 0,
            "independent_clusters": 0,
            "concentration_level": "UNKNOWN",
            "summary": "No sources to analyze.",
        }

    # Score = independent / total
    score = independent / total if total > 0 else 0.0

    summary = (
        f"{total} apparent sources → "
        f"{independent} independent cluster(s). "
        f"Concentration: {concentration}."
    )

    if concentration in ("HIGH", "VERY_HIGH"):
        summary += " High source concentration detected."

    return {
        "score": round(score, 3),
        "total_sources": total,
        "independent_clusters": independent,
        "concentration_level": concentration,
        "summary": summary,
    }


# ============================================================
# MAIN FUNCTION 3: Remove Source Impact Simulate Karo
# ============================================================

def remove_source_impact(
    source_index: int,
    cluster_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    "Yeh source hata toh verdict kya?" — simulate karta hai.

    Input:
        source_index: kaunsa source hatana hai (0-based index)
        cluster_data: cluster_sources() ka output

    Output: {
        "removed_index": int,
        "removed_domain": str,
        "cluster_affected": str,
        "cluster_size": int,
        "sources_remaining": int,
        "clusters_remaining": int,
        "impact": "HIGH / MEDIUM / LOW"
    }
    """
    clusters = cluster_data.get("clusters", [])
    if not clusters:
        return _empty_remove_result(source_index)

    # Dhundo kaunsa cluster is source ko contain karta hai
    affected_cluster = None
    for cluster in clusters:
        if source_index in cluster.get("source_indices", []):
            affected_cluster = cluster
            break

    if not affected_cluster:
        return _empty_remove_result(source_index)

    cluster_size = affected_cluster.get("size", 1)
    total_sources = cluster_data.get("total_sources", 0)
    total_clusters = cluster_data.get("independent_clusters", 0)

    # Agar cluster size = 1, poora cluster remove hoga
    if cluster_size == 1:
        clusters_remaining = total_clusters - 1
        sources_remaining = total_sources - 1
        impact = "HIGH" if clusters_remaining <= 1 else "MEDIUM"
    else:
        # Cluster chhota hoga, lekin exist karega
        clusters_remaining = total_clusters
        sources_remaining = total_sources - 1
        impact = "LOW"

    return {
        "removed_index": source_index,
        "removed_domain": affected_cluster.get("domain", ""),
        "cluster_affected": affected_cluster.get("cluster_id", ""),
        "cluster_size": cluster_size,
        "sources_remaining": sources_remaining,
        "clusters_remaining": clusters_remaining,
        "impact": impact,
    }


# ============================================================
# HELPER: Should Cluster?
# ============================================================

def _should_cluster(a: Dict[str, str], b: Dict[str, str]) -> bool:
    """
    Do sources same cluster mein jaane chahiye ya nahi?

    Rules:
        1. Same domain → same cluster
        2. Title similarity >= threshold → same cluster
    """
    # Rule 1: Same domain
    if SAME_DOMAIN_CLUSTERS:
        domain_a = a.get("domain", "")
        domain_b = b.get("domain", "")
        if domain_a and domain_b and domain_a == domain_b:
            return True

    # Rule 2: Title similarity
    title_a = a.get("title", "").lower()
    title_b = b.get("title", "").lower()

    if title_a and title_b:
        sim = _title_similarity(title_a, title_b)
        if sim >= TITLE_SIMILARITY_THRESHOLD:
            return True

    return False


# ============================================================
# HELPER: Concentration Level
# ============================================================

def _compute_concentration(total: int, independent: int) -> str:
    """Concentration level nikalo."""
    if independent == 0:
        return "UNKNOWN"
    if independent == 1 and total > 3:
        return "VERY_HIGH"
    if independent <= 2 and total > 5:
        return "HIGH"
    if independent <= 3 and total > 8:
        return "MEDIUM"
    return "LOW"


# ============================================================
# HELPER: Title Similarity (Jaccard)
# ============================================================

def _title_similarity(a: str, b: str) -> float:
    """Jaccard similarity between title tokens."""
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)

    return len(intersection) / len(union) if union else 0.0


# ============================================================
# HELPER: Tokenize
# ============================================================

def _tokenize(text: str) -> set:
    """Text ko tokens mein todo (stopwords hataao)."""
    words = re.findall(r"[a-zA-Z0-9]{4,}", text.lower())

    stopwords = {
        "the", "and", "for", "with", "that", "this", "from",
        "was", "were", "are", "has", "have", "had", "not",
        "but", "into", "than", "their", "they", "them", "then",
        "its", "his", "her", "our", "your", "you", "can",
        "could", "would", "should", "may", "might", "will",
        "about", "after", "before", "during", "over", "under",
        "says", "said", "also", "been", "more",
    }

    return {w for w in words if w not in stopwords}


# ============================================================
# HELPER: Normalize Source
# ============================================================

def _normalize_source(item: Any, index: int) -> Dict[str, Any]:
    """Kisi bhi format ke source ko normalize karo."""
    if isinstance(item, dict):
        title = str(item.get("title", "") or item.get("snippet", ""))[:200]
        url = str(item.get("url", "") or item.get("link", ""))
        source = str(item.get("source", ""))
    else:
        metadata = getattr(item, "metadata", {}) or {}
        title = str(metadata.get("title", "") or getattr(item, "page_content", ""))[:200]
        url = str(metadata.get("url", ""))
        source = str(metadata.get("source", ""))

    # URL se domain extract karo
    domain = ""
    if url:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
        except Exception:
            domain = ""

    return {
        "index": index,
        "title": title,
        "url": url,
        "source": source,
        "domain": domain,
    }


# ============================================================
# HELPER: Empty Results
# ============================================================

def _empty_cluster_result() -> Dict[str, Any]:
    """Empty result jab koi source nahi."""
    return {
        "clusters": [],
        "total_sources": 0,
        "independent_clusters": 0,
        "concentration_level": "UNKNOWN",
    }


def _empty_remove_result(source_index: int) -> Dict[str, Any]:
    """Empty result jab remove simulation fail ho."""
    return {
        "removed_index": source_index,
        "removed_domain": "",
        "cluster_affected": "",
        "cluster_size": 0,
        "sources_remaining": 0,
        "clusters_remaining": 0,
        "impact": "UNKNOWN",
    }


# ============================================================
# UI HELPER: Streamlit KPIs
# ============================================================

def get_independence_kpis(cluster_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Streamlit UI ke liye KPI dict.
    UI label: '🔗 Source Independence'
    """
    independence = calculate_independence(cluster_data)
    return {
        "Total Sources": str(cluster_data.get("total_sources", 0)),
        "Independent Clusters": str(cluster_data.get("independent_clusters", 0)),
        "Concentration": str(cluster_data.get("concentration_level", "UNKNOWN")),
        "Independence Score": f"{independence.get('score', 0.0):.2f}",
    }


# ============================================================
# TEST (development ke liye)
# ============================================================

if __name__ == "__main__":
    # Fake sources: same press release ke copies + kuch independent
    test_sources = [
        {"title": "Elon Musk completes Twitter acquisition", "url": "https://reuters.com/article1", "source": "Reuters"},
        {"title": "Elon Musk completes Twitter acquisition", "url": "https://reuters.com/article2", "source": "Reuters"},
        {"title": "Musk finalizes Twitter deal", "url": "https://cnn.com/article1", "source": "CNN"},
        {"title": "Musk finalizes Twitter deal", "url": "https://cnn.com/article2", "source": "CNN"},
        {"title": "Elon Musk buys Twitter for $44B", "url": "https://bbc.com/news1", "source": "BBC"},
        {"title": "Musk closes Twitter purchase", "url": "https://apnews.com/x", "source": "AP"},
        {"title": "Twitter acquisition finalized by Musk", "url": "https://bloomberg.com/y", "source": "Bloomberg"},
        {"title": "Elon Musk completes Twitter acquisition", "url": "https://reuters.com/article3", "source": "Reuters"},
        {"title": "Tech giant Twitter now owned by Musk", "url": "https://nytimes.com/z", "source": "NYTimes"},
        {"title": "Musk finalizes Twitter deal", "url": "https://cnn.com/article3", "source": "CNN"},
        {"title": "Elon Musk acquires Twitter", "url": "https://independent.co.uk/a", "source": "Independent"},
        {"title": "Twitter takeover by Elon Musk complete", "url": "https://theguardian.com/b", "source": "Guardian"},
    ]

    print("=" * 60)
    print("Independence Engine — Self-Test")
    print("=" * 60)

    # Step 1: Clustering
    print("\n[1] Clustering sources...")
    cluster_data = cluster_sources(test_sources)

    print(f"Total sources: {cluster_data['total_sources']}")
    print(f"Independent clusters: {cluster_data['independent_clusters']}")
    print(f"Concentration: {cluster_data['concentration_level']}")

    print("\nClusters:")
    for c in cluster_data["clusters"]:
        print(f"  {c['cluster_id']} (size={c['size']}, domain={c['domain']})")
        print(f"      → {c['representative_title'][:70]}")

    # Step 2: Independence score
    print("\n[2] Calculating independence...")
    independence = calculate_independence(cluster_data)
    print(f"Score: {independence['score']}")
    print(f"Summary: {independence['summary']}")

    # Step 3: Remove source impact
    print("\n[3] Remove source #0 impact...")
    impact = remove_source_impact(0, cluster_data)
    print(f"Removed: {impact['removed_domain']}")
    print(f"Cluster affected: {impact['cluster_affected']} (size={impact['cluster_size']})")
    print(f"Sources remaining: {impact['sources_remaining']}")
    print(f"Clusters remaining: {impact['clusters_remaining']}")
    print(f"Impact: {impact['impact']}")