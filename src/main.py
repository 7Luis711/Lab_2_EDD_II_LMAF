import pandas as pd
import folium
import webbrowser
from airport import Airport
from graph import Graph
from geo_utils import haversine
from algorithms import bfs_connected_components, dijkstra, shortest_path, kruskal_mst


# ======================================================
# CARGA DE DATOS
# ======================================================
def load_data(filepath):
    """Carga los datos del CSV y construye el grafo ponderado."""
    df = pd.read_csv(filepath)
    graph = Graph()

    for _, row in df.iterrows():
        src = Airport(row["Source Airport Code"], row["Source Airport Name"], row["Source Airport City"],
                      row["Source Airport Country"], row["Source Airport Latitude"], row["Source Airport Longitude"])
        dest = Airport(row["Destination Airport Code"], row["Destination Airport Name"], row["Destination Airport City"],
                       row["Destination Airport Country"], row["Destination Airport Latitude"], row["Destination Airport Longitude"])

        graph.add_vertex(src)
        graph.add_vertex(dest)

        dist = haversine(src.latitude, src.longitude, dest.latitude, dest.longitude)
        graph.add_edge(src.code, dest.code, dist)

    return graph


def obtener_peso(graph, code1, code2):
    """Devuelve el peso de la arista si existe en el grafo."""
    for neighbor, weight in graph.get_neighbors(code1):
        if neighbor == code2:
            return weight
    return None


# ======================================================
# MAPAS
# ======================================================
def mostrar_mapa_global(graph, components, nombre_archivo="mapa_global.html", limite_aristas=None, mostrar_distancias=False):
    """
    Dibuja el mapa de la componente principal.
    """
    print("\n Generando mapa global...")

    # Si solo hay una componente (por ejemplo al mostrar una específica)
    if len(components) == 1:
        aeropuertos = list(components[0])
    else:
        # Mostrar solo la componente más grande
        aeropuertos = list(max(components, key=len))

    if not aeropuertos:
        print("No hay aeropuertos en la(s) componente(s) seleccionada(s).")
        return

    first = graph.get_airport(aeropuertos[0])
    mapa = folium.Map(location=[first.latitude, first.longitude], zoom_start=2)

    # Dibujar nodos
    for code in aeropuertos:
        a = graph.get_airport(code)
        folium.CircleMarker(
            [a.latitude, a.longitude],
            radius=3,
            color="red",
            fill=True,
            fill_opacity=0.8,
            tooltip=a.code
        ).add_to(mapa)

    # Dibujar aristas
    seen_edges = set()
    contador = 0

    for code in aeropuertos:
        for neighbor, weight in graph.get_neighbors(code):
            if neighbor not in aeropuertos:
                continue
            edge_key = tuple(sorted([code, neighbor]))
            if edge_key in seen_edges:
                continue
            if limite_aristas is not None and contador >= limite_aristas:
                continue

            a1 = graph.get_airport(code)
            a2 = graph.get_airport(neighbor)

            folium.PolyLine(
                [(a1.latitude, a1.longitude), (a2.latitude, a2.longitude)],
                color="blue",
                weight=2.5,
                opacity=0.6,
                tooltip=f"{a1.code} → {a2.code}: {weight:.2f} km"
            ).add_to(mapa)

            # Mostrar la distancia sobre la línea si se solicita
            if mostrar_distancias:
                lat_mid = (a1.latitude + a2.latitude) / 2
                lon_mid = (a1.longitude + a2.longitude) / 2
                folium.map.Marker(
                    [lat_mid, lon_mid],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:9px; background:rgba(255,255,255,0.8); '
                             f'padding:1px 3px; border-radius:3px;">{int(weight)} km</div>'
                    )
                ).add_to(mapa)

            seen_edges.add(edge_key)
            contador += 1

    mapa.save(nombre_archivo)
    webbrowser.open(nombre_archivo)
    print(f" Mapa generado: {nombre_archivo} (aristas dibujadas: {contador})")


def mostrar_mapa_camino(graph, path, nombre_archivo="mapa_camino.html"):
    """Dibuja el camino mínimo real en el mapa con etiquetas de distancia."""
    if not path or len(path) < 2:
        print("No hay suficientes vértices para dibujar el camino.")
        return

    origen = graph.get_airport(path[0])
    mapa = folium.Map(location=[origen.latitude, origen.longitude], zoom_start=3)

    # Marcadores de cada aeropuerto
    for i, code in enumerate(path):
        a = graph.get_airport(code)
        color = "red" if i == 0 else "green" if i == len(path) - 1 else "blue"
        folium.Marker(
            [a.latitude, a.longitude],
            popup=f"<b>{a.name}</b><br>{a.city}, {a.country}<br>({a.code})",
            tooltip=f"{i+1}. {a.code}",
            icon=folium.Icon(color=color)
        ).add_to(mapa)

    # Dibujar líneas entre tramos reales
    total_distance = 0
    for i in range(len(path) - 1):
        a1 = graph.get_airport(path[i])
        a2 = graph.get_airport(path[i + 1])
        weight = obtener_peso(graph, a1.code, a2.code)

        if weight is None:
            continue

        total_distance += weight
        folium.PolyLine(
            [(a1.latitude, a1.longitude), (a2.latitude, a2.longitude)],
            color="blue",
            weight=4,
            opacity=0.85,
            tooltip=f"{a1.code} → {a2.code}: {weight:.2f} km"
        ).add_to(mapa)

        # Mostrar distancia sobre el tramo
        lat_mid = (a1.latitude + a2.latitude) / 2
        lon_mid = (a1.longitude + a2.longitude) / 2
        folium.map.Marker(
            [lat_mid, lon_mid],
            icon=folium.DivIcon(
                html=f'<div style="font-size:10px; background:rgba(255,255,255,0.9); '
                     f'padding:2px 4px; border-radius:4px;">{int(weight)} km</div>'
            )
        ).add_to(mapa)

    mapa.save(nombre_archivo)
    webbrowser.open(nombre_archivo)
    print(f"\n Mapa del camino generado: {nombre_archivo} (distancia total: {total_distance:.2f} km)")


# ======================================================
# PROGRAMA PRINCIPAL INTERACTIVO
# ======================================================
def main():
    graph = load_data("data/flights_final.csv")
    print(f"✔ Grafo cargado con {len(graph)} aeropuertos.")

    comps = bfs_connected_components(graph)
    print(f"\n[1] El grafo tiene {len(comps)} componente(s):")
    for i, c in enumerate(comps, 1):
        print(f"   - Componente {i}: {len(c)} vértices")

    print("\n[2] Calculando peso del árbol de expansión mínima...")
    for i, comp in enumerate(comps, 1):
        sub = graph.subgraph(comp)
        mst = kruskal_mst(sub)
        print(f"   - Componente {i}: MST = {mst:.2f} km")

    mostrar_mapa_global(graph, comps)

    # Bucle interactivo
    while True:
        print("\n==============================")
        print(" Menú de opciones:")
        print("  1. Consultar nuevo aeropuerto origen")
        print("  2. Consultar camino mínimo (origen → destino)")
        print("  3. Visualizar componente específica")
        print("  4. Salir")
        print("==============================")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            start = input("\nIngrese el código del aeropuerto origen: ").strip().upper()
            a1 = graph.get_airport(start)
            if not a1:
                print(" Aeropuerto no encontrado.")
                continue

            print("\nInformación del aeropuerto origen:")
            for k, v in a1.info().items():
                print(f"   {k}: {v}")

            distances, previous = dijkstra(graph, start)
            reachable = [(c, d) for c, d in distances.items() if d != float("inf") and c != start]
            reachable.sort(key=lambda x: x[1], reverse=True)

            print("\nLos 10 aeropuertos más lejanos (camino mínimo más largo):")
            for i, (code, dist) in enumerate(reachable[:10], 1):
                a = graph.get_airport(code)
                print(f"\n{i}. Información del aeropuerto:")
                print(f"   Código: {a.code}")
                print(f"   Nombre: {a.name}")
                print(f"   Ciudad: {a.city}")
                print(f"   País: {a.country}")
                print(f"   Latitud: {a.latitude}")
                print(f"   Longitud: {a.longitude}")
                print(f"   Distancia del camino: {dist:.2f} km")

        elif opcion == "2":
            start = input("\nIngrese el código del aeropuerto origen: ").strip().upper()
            end = input("Ingrese el código del aeropuerto destino: ").strip().upper()
            distances, previous = dijkstra(graph, start)
            path = shortest_path(previous, start, end)

            if not path:
                print(" No existe camino entre los aeropuertos.")
                continue

            print(f"\nCamino mínimo entre {start} y {end}:")
            total = 0
            for i in range(len(path) - 1):
                a = graph.get_airport(path[i])
                b = graph.get_airport(path[i + 1])
                w = obtener_peso(graph, a.code, b.code)
                if w:
                    print(f"   {a.code} → {b.code}: {w:.2f} km")
                    total += w

            print(f"\n Distancia total del camino: {total:.2f} km")

            if len(path) > 2:
                print("\nInformación de los aeropuertos intermedios:")
                for code in path[1:-1]:
                    a = graph.get_airport(code)
                    for k, v in a.info().items():
                        print(f"   {k}: {v}")
                    print()

            mostrar_mapa_camino(graph, path)

        elif opcion == "3":
            try:
                num = int(input("Ingrese el número de componente a visualizar: "))
                if 1 <= num <= len(comps):
                    comp = comps[num - 1]
                    mostrar_mapa_global(graph, [comp], f"componente_{num}.html", mostrar_distancias=True)
                else:
                    print(" Número de componente inválido.")
            except ValueError:
                print(" Entrada inválida.")

        elif opcion == "4":
            print(" Saliendo del programa...")
            break

        else:
            print(" Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()














