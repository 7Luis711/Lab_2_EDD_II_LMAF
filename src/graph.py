# graph.py
class Graph:
    def __init__(self):
        # Diccionario {codigo_aeropuerto: [(codigo_vecino, peso), ...]}
        self.adjacency = {}
        # Diccionario {codigo_aeropuerto: objeto Airport}
        self.vertices = {}

    def add_vertex(self, airport):
        """Agrega un vértice si no existe aún"""
        if airport.code not in self.adjacency:
            self.adjacency[airport.code] = []
            self.vertices[airport.code] = airport

    def add_edge(self, code1, code2, weight):
        """Agrega una arista no dirigida"""
        if code1 in self.adjacency and code2 in self.adjacency:
            # Evitar duplicados
            if not any(n == code2 for n, _ in self.adjacency[code1]):
                self.adjacency[code1].append((code2, weight))
                self.adjacency[code2].append((code1, weight))

    def get_neighbors(self, code):
        return self.adjacency.get(code, [])

    def get_vertices(self):
        return list(self.adjacency.keys())

    def get_airport(self, code):
        return self.vertices.get(code)

    def __len__(self):
        return len(self.adjacency)
    
    def subgraph(self, vertices_subset):
        """Devuelve un subgrafo que contiene solo los vértices en 'vertices_subset'."""
        sub = Graph()
        for v in vertices_subset:
            if v in self.vertices:
                sub.add_vertex(self.vertices[v])
        for v in vertices_subset:
            for neighbor, weight in self.adjacency.get(v, []):
                if neighbor in vertices_subset:
                    sub.add_edge(v, neighbor, weight)
        return sub
