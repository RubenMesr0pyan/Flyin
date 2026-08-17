
from collections import deque
from typing import Optional


def bfs(graph: dict[str, list[str]], start: str, goal: str) -> Optional[list[str]]:
    if start not in graph:
        return None

    queue = deque([start])
    
    visited = {start}
    
    came_from: dict[str, Optional[str]] = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    return None


def dfs_reachable(graph: dict[str, list[str]], start: str) -> set[str]:
    if start not in graph:
        return set()

    visited = set()
    stack = [start] 

    while stack:
        current = stack.pop()
        
        if current not in visited:
            visited.add(current)
            
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    stack.append(neighbor)

    return visited