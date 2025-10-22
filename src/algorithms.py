# algorithms.py
import heapq

def bfs_connected_components(graph):
    """Devuelve una lista con las componentes conexas del grafo"""
    visited = set()
    components = []

    for start in graph.get_vertices():
        if start not in visited:
            queue = [start]
            component = []
            visited.add(start)

            while queue:
                current = queue.pop(0)
                component.append(current)
                for neighbor, _ in graph.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(component)
    return components


def dijkstra(graph, start):
    """Devuelve las distancias mínimas desde 'start' a todos los vértices"""
    distances = {v: float('inf') for v in graph.get_vertices()}
    previous = {v: None for v in graph.get_vertices()}
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        current_dist, current_vertex = heapq.heappop(pq)
        if current_dist > distances[current_vertex]:
            continue
        for neighbor, weight in graph.get_neighbors(current_vertex):
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))

    return distances, previous


def shortest_path(previous, start, target):
    """Reconstruye el camino más corto desde 'start' hasta 'target'"""
    path = []
    current = target
    while current is not None:
        path.insert(0, current)
        current = previous[current]
    return path if path[0] == start else []


def kruskal_mst(graph):
    """Calcula el peso del árbol de expansión mínima (Kruskal)"""
    parent = {}
    rank = {}

    def find(v):
        if parent[v] != v:
            parent[v] = find(parent[v])
        return parent[v]

    def union(v1, v2):
        root1, root2 = find(v1), find(v2)
        if root1 != root2:
            if rank[root1] < rank[root2]:
                parent[root1] = root2
            else:
                parent[root2] = root1
                if rank[root1] == rank[root2]:
                    rank[root1] += 1

    for v in graph.get_vertices():
        parent[v] = v
        rank[v] = 0

    edges = []
    for v in graph.get_vertices():
        for neighbor, weight in graph.get_neighbors(v):
            if (neighbor, v, weight) not in edges:
                edges.append((v, neighbor, weight))

    edges.sort(key=lambda x: x[2])

    mst_weight = 0
    for v1, v2, weight in edges:
        if find(v1) != find(v2):
            union(v1, v2)
            mst_weight += weight

    return mst_weight
