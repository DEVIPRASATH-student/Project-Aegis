"""
Project Aegis -- Graph-Based Fraud Intelligence Engine

Uses NetworkX to model a financial account relationship network.
Computes multiple graph-based risk signals:
  - Shortest-path distance to known scammer/mule accounts (3-hop rule)
  - PageRank centrality (accounts central to suspicious subnetworks)
  - Degree centrality (accounts with unusually many connections)
  - Clustering coefficient (tightly connected fraud rings)
  - Community detection for fraud cluster identification

The graph contains 50+ nodes representing legitimate users, merchants,
mule accounts, and known scammers with 100+ realistic transaction edges.
"""

import networkx as nx
from typing import Dict, Any, Optional, List, Set
import json


class FraudGraphEngine:
    """
    Financial account relationship graph for fraud proximity analysis.

    Builds a realistic synthetic network of accounts and their
    transaction/relationship edges. Used to evaluate how close
    a given receiver is to known fraudulent accounts.
    """

    # Alias map: realistic account numbers → graph node IDs
    # This lets the frontend send human-readable account numbers
    # while the graph engine uses short internal node IDs.
    ACCOUNT_ALIASES: Dict[str, str] = {
        "XXXX4821": "B",
        "XXXX 4821": "B",
    }

    def __init__(self):
        self.graph = nx.DiGraph()
        self._known_scammers: Set[str] = set()
        self._known_mules: Set[str] = set()
        self._legitimate_accounts: Set[str] = set()
        self._merchants: Set[str] = set()
        self._build_network()

    def resolve_alias(self, account: str) -> str:
        """Resolve an account alias to its graph node ID."""
        return self.ACCOUNT_ALIASES.get(account, account)

    def _build_network(self):
        """
        Construct the synthetic financial network.

        Network topology:
        - 15 legitimate user accounts (L01-L15)
        - 8 merchant accounts (M01-M08)
        - 10 mule/intermediary accounts (MULE_01-MULE_10)
        - 5 known scammer accounts (SCAMMER_01-SCAMMER_05)
        - Demo accounts (A, B, C, D) woven into the network
        - 20+ additional accounts for network density
        """

        # ── Known Scammer Accounts ────────────────────────────────
        scammers = [
            "SCAMMER_01", "SCAMMER_02", "SCAMMER_03",
            "SCAMMER_04", "SCAMMER_05",
        ]
        for s in scammers:
            self.graph.add_node(s, account_type="scammer", flagged=True, risk_tag="confirmed_fraud")
            self._known_scammers.add(s)

        # ── Mule / Intermediary Accounts ──────────────────────────
        mules = [
            "MULE_01", "MULE_02", "MULE_03", "MULE_04", "MULE_05",
            "MULE_06", "MULE_07", "MULE_08", "MULE_09", "MULE_10",
        ]
        for m in mules:
            self.graph.add_node(m, account_type="mule", flagged=True, risk_tag="suspected_mule")
            self._known_mules.add(m)

        # ── Legitimate User Accounts ──────────────────────────────
        legit_users = [f"L{i:02d}" for i in range(1, 16)]
        for u in legit_users:
            self.graph.add_node(u, account_type="legitimate", flagged=False, risk_tag="clean")
            self._legitimate_accounts.add(u)

        # ── Merchant Accounts ─────────────────────────────────────
        merchants = [f"M{i:02d}" for i in range(1, 9)]
        for m in merchants:
            self.graph.add_node(m, account_type="merchant", flagged=False, risk_tag="verified_merchant")
            self._merchants.add(m)

        # ── Demo Accounts (the ones used in the hackathon demo) ───
        # A = Dad (victim/sender)
        # B = Receiver (the one the scammer told Dad to send money to)
        # C, D = Intermediaries connecting B to the fraud network
        self.graph.add_node("A", account_type="legitimate", flagged=False, risk_tag="clean", label="Dad")
        self.graph.add_node("B", account_type="suspicious", flagged=False, risk_tag="unknown", label="XXXX4821")
        self.graph.add_node("C", account_type="intermediary", flagged=False, risk_tag="suspected_intermediary")
        self.graph.add_node("D", account_type="mule", flagged=True, risk_tag="suspected_mule")

        self._legitimate_accounts.add("A")
        self._known_mules.add("D")

        # ── Additional accounts for network density ───────────────
        extra_accounts = [f"X{i:02d}" for i in range(1, 21)]
        for x in extra_accounts:
            self.graph.add_node(x, account_type="unknown", flagged=False, risk_tag="unverified")

        # ── Build Transaction/Relationship Edges ──────────────────
        self._build_edges()

    def _build_edges(self):
        """
        Create realistic transaction and relationship edges.
        Edge weights represent transaction frequency/volume.
        """

        # ── FRAUD CHAIN 1: The Demo Chain ─────────────────────────
        # A -> B -> C -> D -> SCAMMER_01
        # This is the primary demo path (3 hops from B to SCAMMER_01)
        self.graph.add_edge("A", "B", weight=1, tx_type="transfer")
        self.graph.add_edge("B", "C", weight=5, tx_type="transfer")
        self.graph.add_edge("C", "D", weight=8, tx_type="transfer")
        self.graph.add_edge("D", "SCAMMER_01", weight=12, tx_type="transfer")

        # ── FRAUD CHAIN 2: Secondary Fraud Ring ───────────────────
        # MULE_01 -> MULE_02 -> SCAMMER_02
        # MULE_01 -> MULE_03 -> MULE_04 -> SCAMMER_03
        self.graph.add_edge("MULE_01", "MULE_02", weight=7, tx_type="transfer")
        self.graph.add_edge("MULE_02", "SCAMMER_02", weight=15, tx_type="transfer")
        self.graph.add_edge("MULE_01", "MULE_03", weight=4, tx_type="transfer")
        self.graph.add_edge("MULE_03", "MULE_04", weight=6, tx_type="transfer")
        self.graph.add_edge("MULE_04", "SCAMMER_03", weight=10, tx_type="transfer")

        # ── FRAUD CHAIN 3: Complex Layering Network ───────────────
        # Multiple mules feeding into SCAMMER_04 and SCAMMER_05
        self.graph.add_edge("MULE_05", "MULE_06", weight=9, tx_type="transfer")
        self.graph.add_edge("MULE_06", "SCAMMER_04", weight=11, tx_type="transfer")
        self.graph.add_edge("MULE_07", "MULE_08", weight=3, tx_type="transfer")
        self.graph.add_edge("MULE_08", "MULE_09", weight=5, tx_type="transfer")
        self.graph.add_edge("MULE_09", "SCAMMER_05", weight=8, tx_type="transfer")
        self.graph.add_edge("MULE_10", "SCAMMER_05", weight=13, tx_type="transfer")

        # Cross-links between fraud chains (realistic -- fraud rings overlap)
        self.graph.add_edge("D", "MULE_01", weight=3, tx_type="transfer")
        self.graph.add_edge("MULE_04", "MULE_05", weight=2, tx_type="transfer")
        self.graph.add_edge("MULE_06", "MULE_09", weight=4, tx_type="transfer")
        self.graph.add_edge("C", "MULE_07", weight=1, tx_type="transfer")

        # B has connections to suspicious network via other paths too
        self.graph.add_edge("B", "MULE_01", weight=2, tx_type="transfer")
        self.graph.add_edge("B", "X01", weight=1, tx_type="transfer")

        # ── LEGITIMATE TRANSACTION PATTERNS ───────────────────────
        # Normal users transacting with merchants
        legit_edges = [
            ("L01", "M01"), ("L01", "M02"), ("L01", "L02"),
            ("L02", "M01"), ("L02", "M03"), ("L02", "L03"),
            ("L03", "M02"), ("L03", "M04"), ("L03", "L04"),
            ("L04", "M03"), ("L04", "M05"), ("L04", "L05"),
            ("L05", "M04"), ("L05", "M06"), ("L05", "L06"),
            ("L06", "M05"), ("L06", "M07"), ("L06", "L07"),
            ("L07", "M06"), ("L07", "M08"), ("L07", "L08"),
            ("L08", "M07"), ("L08", "L09"),
            ("L09", "M08"), ("L09", "L10"),
            ("L10", "M01"), ("L10", "L11"),
            ("L11", "M02"), ("L11", "L12"),
            ("L12", "M03"), ("L12", "L13"),
            ("L13", "M04"), ("L13", "L14"),
            ("L14", "M05"), ("L14", "L15"),
            ("L15", "M06"), ("L15", "L01"),
        ]
        for src, dst in legit_edges:
            self.graph.add_edge(src, dst, weight=1, tx_type="legitimate")

        # A (Dad) has normal legitimate transaction history
        self.graph.add_edge("A", "M01", weight=1, tx_type="legitimate")
        self.graph.add_edge("A", "M02", weight=1, tx_type="legitimate")
        self.graph.add_edge("A", "L01", weight=2, tx_type="legitimate")
        self.graph.add_edge("A", "L05", weight=1, tx_type="legitimate")

        # ── Extra account edges for density ───────────────────────
        extra_edges = [
            ("X01", "X02"), ("X02", "X03"), ("X03", "X04"),
            ("X04", "X05"), ("X05", "X06"), ("X06", "X07"),
            ("X07", "X08"), ("X08", "X09"), ("X09", "X10"),
            ("X10", "X11"), ("X11", "X12"), ("X12", "X13"),
            ("X13", "X14"), ("X14", "X15"), ("X15", "X16"),
            ("X16", "X17"), ("X17", "X18"), ("X18", "X19"),
            ("X19", "X20"), ("X20", "X01"),
            # Some extra accounts connect to legitimate network
            ("X01", "L01"), ("X05", "L05"), ("X10", "L10"),
            ("X15", "M01"), ("X20", "M05"),
            # A few extra accounts have weak connections to fraud
            ("X03", "MULE_05"), ("X08", "MULE_10"),
        ]
        for src, dst in extra_edges:
            self.graph.add_edge(src, dst, weight=1, tx_type="unknown")

    def _get_all_flagged_accounts(self) -> Set[str]:
        """Return all accounts tagged as scammers or mules."""
        return self._known_scammers | self._known_mules

    def calculate_shortest_path_to_risk(self, account: str) -> Dict[str, Any]:
        """
        Calculate the shortest-path distance from a given account
        to any known scammer account.

        Returns the minimum hop count and the nearest scammer.
        Uses undirected view for path calculation (money can flow
        in either direction in the relationship graph).
        """
        if account not in self.graph:
            return {
                "hops": -1,
                "nearest_scammer": None,
                "path": [],
                "reachable": False,
            }

        undirected = self.graph.to_undirected()
        min_hops = float("inf")
        nearest_scammer = None
        shortest_path = []

        for scammer in self._known_scammers:
            if scammer not in undirected:
                continue
            try:
                path = nx.shortest_path(undirected, account, scammer)
                hops = len(path) - 1
                if hops < min_hops:
                    min_hops = hops
                    nearest_scammer = scammer
                    shortest_path = path
            except nx.NetworkXNoPath:
                continue

        if min_hops == float("inf"):
            return {
                "hops": -1,
                "nearest_scammer": None,
                "path": [],
                "reachable": False,
            }

        return {
            "hops": min_hops,
            "nearest_scammer": nearest_scammer,
            "path": shortest_path,
            "reachable": True,
        }

    def calculate_pagerank(self, account: str) -> float:
        """
        Calculate PageRank score for the account.
        Higher PageRank in a fraud-heavy subnetwork indicates
        the account may be central to money movement.
        """
        if account not in self.graph:
            return 0.0
        try:
            pr = nx.pagerank(self.graph, alpha=0.85)
            return pr.get(account, 0.0)
        except Exception:
            return 0.0

    def calculate_degree_centrality(self, account: str) -> float:
        """
        Calculate degree centrality for the account.
        Accounts with many connections relative to network size
        may indicate mule activity (collecting/distributing funds).
        """
        if account not in self.graph:
            return 0.0
        try:
            dc = nx.degree_centrality(self.graph)
            return dc.get(account, 0.0)
        except Exception:
            return 0.0

    def calculate_clustering_coefficient(self, account: str) -> float:
        """
        Calculate clustering coefficient.
        High clustering indicates the account is part of a
        tightly connected group (potential fraud ring).
        """
        if account not in self.graph:
            return 0.0
        try:
            undirected = self.graph.to_undirected()
            return nx.clustering(undirected, account)
        except Exception:
            return 0.0

    def detect_fraud_community(self, account: str) -> Dict[str, Any]:
        """
        Use community detection (greedy modularity) to identify
        whether the account belongs to the same community as
        known fraudulent accounts.
        """
        if account not in self.graph:
            return {"in_fraud_community": False, "community_id": -1, "community_has_scammers": False}

        try:
            undirected = self.graph.to_undirected()
            communities = list(nx.community.greedy_modularity_communities(undirected))

            account_community_id = -1
            account_community = set()
            for i, community in enumerate(communities):
                if account in community:
                    account_community_id = i
                    account_community = community
                    break

            # Check if any known scammers or mules are in the same community
            scammers_in_community = account_community & self._known_scammers
            mules_in_community = account_community & self._known_mules
            has_fraud = len(scammers_in_community) > 0 or len(mules_in_community) > 0

            return {
                "in_fraud_community": has_fraud,
                "community_id": account_community_id,
                "community_size": len(account_community),
                "community_has_scammers": len(scammers_in_community) > 0,
                "community_has_mules": len(mules_in_community) > 0,
                "scammers_in_community": len(scammers_in_community),
                "mules_in_community": len(mules_in_community),
            }
        except Exception:
            return {"in_fraud_community": False, "community_id": -1, "community_has_scammers": False}

    def calculate_receiver_risk(self, receiver: str) -> Dict[str, Any]:
        """
        Comprehensive risk assessment for a receiver account.

        Combines all graph-based signals into a structured result
        that the risk scorer can use as features.

        Args:
            receiver: The account identifier to evaluate.

        Returns:
            Dictionary with all computed graph risk signals.
        """
        # Resolve alias (e.g. "XXXX4821" → "B") before graph lookup
        resolved = self.resolve_alias(receiver)
        path_info = self.calculate_shortest_path_to_risk(resolved)
        pagerank = self.calculate_pagerank(resolved)
        degree_centrality = self.calculate_degree_centrality(resolved)
        clustering = self.calculate_clustering_coefficient(resolved)
        community_info = self.detect_fraud_community(resolved)

        # Compute a graph-based sub-score (0-100)
        graph_score = 0.0

        # Shortest path contribution (major factor)
        hops = path_info["hops"]
        if hops == -1 or not path_info["reachable"]:
            path_score = 5.0  # Unknown accounts get small baseline risk
        elif hops <= 1:
            path_score = 100.0
        elif hops <= 2:
            path_score = 85.0
        elif hops <= 3:
            path_score = 65.0
        elif hops <= 4:
            path_score = 40.0
        elif hops <= 5:
            path_score = 20.0
        else:
            path_score = 10.0

        # Normalize PageRank (compare to network average)
        all_pr = nx.pagerank(self.graph, alpha=0.85)
        avg_pr = sum(all_pr.values()) / len(all_pr) if all_pr else 0.001
        pr_ratio = pagerank / avg_pr if avg_pr > 0 else 0
        pr_score = min(pr_ratio * 25, 100.0)

        # Community membership contribution
        community_score = 0.0
        if community_info.get("community_has_scammers"):
            community_score = 40.0
        elif community_info.get("community_has_mules"):
            community_score = 25.0
        elif community_info.get("in_fraud_community"):
            community_score = 15.0

        # Weighted combination for graph sub-score
        graph_score = (
            path_score * 0.50 +
            pr_score * 0.15 +
            community_score * 0.25 +
            (clustering * 100) * 0.10
        )
        graph_score = min(max(graph_score, 0.0), 100.0)

        # Determine risk level from graph alone
        if graph_score >= 70:
            graph_risk_level = "HIGH"
        elif graph_score >= 40:
            graph_risk_level = "MEDIUM"
        else:
            graph_risk_level = "LOW"

        account_type = "unknown"
        if resolved in self.graph:
            account_type = self.graph.nodes[resolved].get("account_type", "unknown")

        return {
            "receiver": receiver,
            "graph_risk_score": round(graph_score, 2),
            "graph_risk_level": graph_risk_level,
            "hops_to_known_risk": hops,
            "nearest_flagged_account": path_info["nearest_scammer"],
            "path_to_risk": path_info["path"],
            "reachable_from_fraud": path_info["reachable"],
            "pagerank": round(pagerank, 6),
            "degree_centrality": round(degree_centrality, 4),
            "clustering_coefficient": round(clustering, 4),
            "in_fraud_community": community_info.get("in_fraud_community", False),
            "community_has_scammers": community_info.get("community_has_scammers", False),
            "community_has_mules": community_info.get("community_has_mules", False),
            "account_type": account_type,
        }

    def is_known_account(self, account: str) -> bool:
        """Check if the account exists in the graph."""
        return self.resolve_alias(account) in self.graph

    def get_network_stats(self) -> Dict[str, Any]:
        """Return overall network statistics for the dashboard."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "known_scammers": len(self._known_scammers),
            "known_mules": len(self._known_mules),
            "legitimate_accounts": len(self._legitimate_accounts),
            "merchants": len(self._merchants),
        }


# Module-level singleton instance
_engine_instance: Optional[FraudGraphEngine] = None


def get_graph_engine() -> FraudGraphEngine:
    """Get or create the singleton graph engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = FraudGraphEngine()
    return _engine_instance
