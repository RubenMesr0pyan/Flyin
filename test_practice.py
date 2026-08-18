"""Tests for Day 2 graph traversal warm-up (BFS and DFS)."""
import pytest
from practice import bfs, dfs_reachable


def test_bfs_shortest_path_simple() -> None:
    """Test that BFS finds the shortest path by edge count."""
    graph = {
        "Start": ["A", "B"],
        "A": ["Start", "C"],
        "B": ["Start", "C", "End"],
        "C": ["A", "B", "End"],
        "End": ["B", "C"],
    }
    path = bfs(graph, "Start", "End")
    assert path == ["Start", "B", "End"]


def test_bfs_no_path() -> None:
    """Test that BFS returns None when no path exists to the goal."""
    graph = {
        "Start": ["A"],
        "A": [],
        "Isolated": ["End"],
        "End": [],
    }
    path = bfs(graph, "Start", "End")
    assert path is None


def test_bfs_start_equals_goal() -> None:
    """Test BFS when start and goal are the same node."""
    graph = {"Start": ["A"], "A": []}
    path = bfs(graph, "Start", "Start")
    assert path == ["Start"]


def test_dfs_reachable_all() -> None:
    """Test DFS finds all reachable nodes, ignoring unreachable ones and handling cycles."""
    graph = {
        "Start": ["A", "B"],
        "A": ["B", "Start"],
        "B": ["End"],
        "End": [],
        "Isolated": ["Somewhere"],
        "Somewhere": [],
    }
    reachable = dfs_reachable(graph, "Start")
    assert reachable == {"Start", "A", "B", "End"}


def test_dfs_reachable_empty() -> None:
    """Test DFS starting from a non-existent node returns an empty set."""
    graph = {"A": ["B"], "B": []}
    reachable = dfs_reachable(graph, "Missing")
    assert reachable == set()