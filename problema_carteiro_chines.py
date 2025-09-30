import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

def find_odd_degree_vertices(graph):
    """Encontra os vértices de grau ímpar no grafo."""
    odd_degree_vertices = []
    for node in graph.nodes():
        if graph.degree(node) % 2 != 0:
            odd_degree_vertices.append(node)
    return odd_degree_vertices

def add_minimum_weight_matching(graph):
    """
    Adiciona arestas ao grafo para torná-lo euleriano.
    
    Encontra o emparelhamento de peso mínimo entre os vértices de grau ímpar
    e adiciona arestas duplicadas ao grafo para tornar todos os vértices de grau par.
    """
    # Encontra os vértices de grau ímpar
    odd_vertices = find_odd_degree_vertices(graph)
    
    if not odd_vertices:
        return graph.copy(), 0  # O grafo já é euleriano
    
    # Cria um grafo completo com os vértices de grau ímpar
    complete_graph = nx.Graph()
    
    # Para cada par de vértices de grau ímpar, encontra o caminho mais curto
    for u, v in combinations(odd_vertices, 2):
        if nx.has_path(graph, u, v):
            # Encontra o caminho mais curto entre u e v
            path_length = nx.shortest_path_length(graph, u, v, weight='weight')
            complete_graph.add_edge(u, v, weight=path_length)
    
    # Encontra o emparelhamento de peso mínimo
    matching = nx.algorithms.matching.min_weight_matching(complete_graph)
    
    # Cria uma cópia do grafo original para adicionar as arestas duplicadas
    eulerian_graph = nx.MultiGraph()
    
    # Primeiro, adiciona todas as arestas originais
    for u, v, data in graph.edges(data=True):
        eulerian_graph.add_edge(u, v, **data)
    
    # Adiciona as arestas do emparelhamento ao grafo
    added_weight = 0
    for u, v in matching:
        # Encontra o caminho mais curto entre u e v no grafo original
        path = nx.shortest_path(graph, u, v, weight='weight')
        
        # Adiciona cada aresta do caminho ao grafo euleriano
        for i in range(len(path) - 1):
            node1, node2 = path[i], path[i + 1]
            weight = graph[node1][node2]['weight']
            
            # Adiciona a aresta duplicada
            eulerian_graph.add_edge(node1, node2, weight=weight)
            added_weight += weight
    
    return eulerian_graph, added_weight

def find_eulerian_circuit(graph, start_node=None):
    """Encontra um circuito euleriano no grafo."""
    if not nx.is_eulerian(graph):
        raise nx.NetworkXError("O grafo não é euleriano. Verifique a conectividade e os graus dos vértices.")
    
    if start_node is None:
        start_node = list(graph.nodes())[0]
    
    return list(nx.eulerian_circuit(graph, source=start_node))

def solve_chinese_postman(graph, start_node=None):
    """
    Resolve o Problema do Carteiro Chinês.
    
    Retorna um dicionário com o custo total da rota e o circuito euleriano.
    """
    # Calcula o custo total das arestas originais
    original_cost = sum(graph[u][v]['weight'] for u, v in graph.edges())
    
    # Adiciona arestas para tornar o grafo euleriano
    eulerian_graph, added_cost = add_minimum_weight_matching(graph)
    
    # Encontra um circuito euleriano
    circuit = find_eulerian_circuit(eulerian_graph, start_node)
    
    # Formata o circuito para incluir os pesos das arestas
    formatted_circuit = []
    for u, v in circuit:
        # Para MultiGraph, precisamos pegar o peso da primeira aresta entre u e v
        weight = eulerian_graph[u][v][0]['weight'] if isinstance(eulerian_graph, nx.MultiGraph) else eulerian_graph[u][v]['weight']
        formatted_circuit.append((u, v, {'weight': weight}))
    
    # Calcula o custo total da rota
    total_cost = original_cost + added_cost
    
    return {
        'total_cost': total_cost,
        'circuit': formatted_circuit
    }

def draw_graph(graph, title="Grafo", with_labels=True, node_color='lightblue', edge_color='black'):
    """Desenha o grafo usando matplotlib."""
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph, seed=42)  # Posicionamento dos nós
    
    # Extrai os pesos das arestas para usar como labels
    if isinstance(graph, nx.MultiGraph):
        edge_labels = {}
        for u, v, k, data in graph.edges(data=True, keys=True):
            if (u, v) in edge_labels:
                edge_labels[(u, v)] += data['weight']
            else:
                edge_labels[(u, v)] = data['weight']
    else:
        edge_labels = {(u, v): data['weight'] for u, v, data in graph.edges(data=True)}
    
    # Desenha o grafo
    nx.draw(graph, pos, with_labels=with_labels, node_color=node_color, 
            node_size=500, font_size=12, font_weight='bold', edge_color=edge_color)
    
    # Adiciona os pesos das arestas como labels
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    
    plt.title(title)
    plt.axis('off')
    return plt

def visualize_circuit(graph, circuit, title="Circuito Euleriano"):
    """Visualiza o circuito euleriano no grafo."""
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph, seed=42)
    
    # Desenha o grafo base
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', 
            node_size=500, font_size=12, font_weight='bold', edge_color='gray', width=1)
    
    # Desenha o circuito com cores diferentes
    edges = [(u, v) for u, v, _ in circuit]
    
    # Para MultiGraph, precisamos desenhar as arestas de forma diferente
    if isinstance(graph, nx.MultiGraph):
        # Não podemos usar nx.draw_networkx_edges diretamente para MultiGraph
        # Então vamos desenhar cada aresta individualmente
        for i, (u, v, _) in enumerate(circuit):
            nx.draw_networkx_edges(graph, pos, edgelist=[(u, v)], edge_color='red', 
                                  width=2, alpha=0.7)
    else:
        nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color='red', width=2)
    
    # Adiciona os pesos das arestas como labels
    if isinstance(graph, nx.MultiGraph):
        edge_labels = {}
        for u, v, k, data in graph.edges(data=True, keys=True):
            if (u, v) in edge_labels:
                edge_labels[(u, v)] += data['weight']
            else:
                edge_labels[(u, v)] = data['weight']
    else:
        edge_labels = {(u, v): data['weight'] for u, v, data in graph.edges(data=True)}
    
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    
    plt.title(title)
    plt.axis('off')
    return plt

if __name__ == "__main__":
    # Exemplo 1: Grafo com vértices de grau ímpar
    G = nx.Graph()
    G.add_edge('A', 'B', weight=10)
    G.add_edge('A', 'C', weight=15)
    G.add_edge('B', 'D', weight=20)
    G.add_edge('C', 'D', weight=25)
    G.add_edge('C', 'E', weight=30)
    G.add_edge('D', 'E', weight=10)
    G.add_edge('E', 'F', weight=12)
    G.add_edge('F', 'A', weight=5)

    print("Grafo original (arestas e pesos):")
    for u, v, data in G.edges(data=True):
        print(f"  {u} -- {v} (peso: {data['weight']})")

    print("\nGraus dos vértices do grafo original:")
    for node in G.nodes():
        print(f"  Vértice {node}: Grau {G.degree(node)}")

    # Identifica os vértices de grau ímpar
    odd_vertices = find_odd_degree_vertices(G)
    print(f"\nVértices de grau ímpar: {odd_vertices}")

    # Resolve o Problema do Carteiro Chinês
    solution = solve_chinese_postman(G, start_node='A')

    print("\nResultado do Problema do Carteiro Chinês:")
    print(f"Custo total da rota: {solution['total_cost']}")
    print("Sequência de arestas a serem percorridas (circuito euleriano):")
    
    for edge in solution['circuit']:
        print(f"  {edge[0]} -- {edge[1]} (peso: {edge[2]['weight']})")

    # Salva o grafo original como imagem
    plt_original = draw_graph(G, title="Grafo Original")
    plt_original.savefig("grafo_original.png")
    
    # Cria o grafo euleriano para visualização
    eulerian_graph, _ = add_minimum_weight_matching(G)
    plt_eulerian = draw_graph(eulerian_graph, title="Grafo Euleriano (com arestas duplicadas)")
    plt_eulerian.savefig("grafo_euleriano.png")
    
    # Visualiza o circuito euleriano
    plt_circuit = visualize_circuit(eulerian_graph, solution['circuit'], title="Circuito Euleriano")
    plt_circuit.savefig("circuito_euleriano.png")

    print("\n--- Exemplo 2: Grafo já euleriano ---")
    G2 = nx.Graph()
    G2.add_edge('A', 'B', weight=1)
    G2.add_edge('B', 'C', weight=1)
    G2.add_edge('C', 'D', weight=1)
    G2.add_edge('D', 'A', weight=1)

    print("Grafo 2 original (arestas e pesos):")
    for u, v, data in G2.edges(data=True):
        print(f"  {u} -- {v} (peso: {data['weight']})")

    print("\nGraus dos vértices do grafo 2 original:")
    for node in G2.nodes():
        print(f"  Vértice {node}: Grau {G2.degree(node)}")

    solution2 = solve_chinese_postman(G2, start_node='A')
    print("\nResultado do Problema do Carteiro Chinês (Grafo 2):")
    print(f"Custo total da rota: {solution2['total_cost']}")
    print("Sequência de arestas a serem percorridas:")
    for edge in solution2['circuit']:
        print(f"  {edge[0]} -- {edge[1]} (peso: {edge[2]['weight']})")

    # Salva o grafo 2 como imagem
    plt_g2 = draw_graph(G2, title="Grafo 2 (já euleriano)")
    plt_g2.savefig("grafo2_euleriano.png")
    
    # Visualiza o circuito euleriano do grafo 2
    plt_circuit2 = visualize_circuit(G2, solution2['circuit'], title="Circuito Euleriano (Grafo 2)")
    plt_circuit2.savefig("circuito_euleriano_grafo2.png")

    print("\n--- Exemplo 3: Grafo com vértices ímpares ---")
    G3 = nx.Graph()
    G3.add_edge('A', 'B', weight=1)
    G3.add_edge('B', 'C', weight=2)
    G3.add_edge('C', 'D', weight=3)
    G3.add_edge('D', 'E', weight=4)
    G3.add_edge('E', 'A', weight=5)
    G3.add_edge('A', 'D', weight=6)

    print("Grafo 3 original (arestas e pesos):")
    for u, v, data in G3.edges(data=True):
        print(f"  {u} -- {v} (peso: {data['weight']})")

    print("\nGraus dos vértices do grafo 3 original:")
    for node in G3.nodes():
        print(f"  Vértice {node}: Grau {G3.degree(node)}")

    # Identifica os vértices de grau ímpar no grafo 3
    odd_vertices3 = find_odd_degree_vertices(G3)
    print(f"\nVértices de grau ímpar no grafo 3: {odd_vertices3}")

    solution3 = solve_chinese_postman(G3, start_node='A')
    print("\nResultado do Problema do Carteiro Chinês (Grafo 3):")
    print(f"Custo total da rota: {solution3['total_cost']}")
    print("Sequência de arestas a serem percorridas:")
    for edge in solution3['circuit']:
        print(f"  {edge[0]} -- {edge[1]} (peso: {edge[2]['weight']})")

    # Salva o grafo 3 como imagem
    plt_g3 = draw_graph(G3, title="Grafo 3 (com vértices de grau ímpar)")
    plt_g3.savefig("grafo3_original.png")
    
    # Cria o grafo euleriano 3 para visualização
    eulerian_graph3, _ = add_minimum_weight_matching(G3)
    plt_eulerian3 = draw_graph(eulerian_graph3, title="Grafo 3 Euleriano (com arestas duplicadas)")
    plt_eulerian3.savefig("grafo3_euleriano.png")
    
    # Visualiza o circuito euleriano do grafo 3
    plt_circuit3 = visualize_circuit(eulerian_graph3, solution3['circuit'], title="Circuito Euleriano (Grafo 3)")
    plt_circuit3.savefig("circuito_euleriano_grafo3.png")

    print("\nImagens salvas: grafo_original.png, grafo_euleriano.png, circuito_euleriano.png")
    print("Imagens do grafo 2: grafo2_euleriano.png, circuito_euleriano_grafo2.png")
    print("Imagens do grafo 3: grafo3_original.png, grafo3_euleriano.png, circuito_euleriano_grafo3.png")

