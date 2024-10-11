import pygame
import random
import heapq
import math

pygame.init()

#colores
WHITE = (240, 240, 240)
BLACK = (50, 50, 50)
BLUE = (100, 149, 237)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
EDGE_COLOR = (169, 169, 169)
PATH_COLOR = (255, 165, 0)

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Optimización de Rutas en un Sistema Urbano")

NODE_RADIUS = 10
NODE_COLOR = BLUE
FONT = pygame.font.Font(None, 22)

class Node:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name

    def draw(self, screen, color=NODE_COLOR):
        pygame.draw.circle(screen, color, (self.x, self.y), NODE_RADIUS)
        text = FONT.render(self.name, True, BLACK)
        screen.blit(text, (self.x - 15, self.y - 15))

    def is_mouse_over(self, mouse_pos):
        return (self.x - NODE_RADIUS <= mouse_pos[0] <= self.x + NODE_RADIUS and
                self.y - NODE_RADIUS <= mouse_pos[1] <= mouse_pos[1] + NODE_RADIUS)

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = {}

    def add_node(self, x, y, name):
        node = Node(x, y, name)
        self.nodes.append(node)
        self.edges[name] = {}

    def add_edge(self, from_node, to_node, cost):
        self.edges[from_node][to_node] = cost
        self.edges[to_node][from_node] = cost

    def draw(self, screen):
        for from_node, neighbors in self.edges.items():
            for to_node, cost in neighbors.items():
                from_pos = self.get_node_pos(from_node)
                to_pos = self.get_node_pos(to_node)
                pygame.draw.line(screen, EDGE_COLOR, from_pos, to_pos, 2)

                mid_pos = ((from_pos[0] + to_pos[0]) // 2, (from_pos[1] + to_pos[1]) // 2 - 20) 
                text = FONT.render(f"{cost} min", True, BLACK)
                screen.blit(text, mid_pos)

        for node in self.nodes:
            node.draw(screen)

    def get_node_pos(self, name):
        for node in self.nodes:
            if node.name == name:
                return node.x, node.y
        return None

def heuristic(node_pos, goal_pos):
    return math.dist(node_pos, goal_pos)

def simulate_traffic(graph):
    for from_node, neighbors in graph.edges.items():
        for to_node in neighbors:
            original_cost = graph.edges[from_node][to_node]
            traffic_factor = random.uniform(0.8, 1.4)
            new_cost = round(original_cost * traffic_factor, 2)
            graph.edges[from_node][to_node] = new_cost 

def a_star_search(graph, start, goal):
    open_list = []
    heapq.heappush(open_list, (0, start))
    
    g_costs = {start: 0}
    came_from = {start: None}
    
    while open_list:
        current_cost, current_node = heapq.heappop(open_list)

        if current_node == goal:
            path = []
            while current_node:
                path.append(current_node)
                current_node = came_from[current_node]
            return path[::-1]

        for neighbor, cost in graph.edges[current_node].items():
            tentative_g_cost = g_costs[current_node] + cost

            if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                g_costs[neighbor] = tentative_g_cost
                f_cost = tentative_g_cost + heuristic(graph.get_node_pos(neighbor), graph.get_node_pos(goal))
                heapq.heappush(open_list, (f_cost, neighbor))
                came_from[neighbor] = current_node
    
    return None

def main():
    clock = pygame.time.Clock()

    graph = Graph()
    locations = [
    ('Lima', 100, 100), ('Cusco', 300, 150), ('Arequipa', 500, 100),
    ('Trujillo', 200, 300), ('Piura', 500, 300), ('Ica', 400, 200),
    ('Chiclayo', 600, 150), ('Tacna', 450, 250), ('Puno', 600, 250),
    ('Huancayo', 700, 400), ('Cajamarca', 500, 400), ('Ayacucho', 350, 400),
    ('Moquegua', 150, 400), ('Tumbes', 300, 400), ('Tarapoto', 700, 100)
    ]

    for loc in locations:
        graph.add_node(loc[1], loc[2], loc[0])

    connections = [
        ('Lima', 'Cusco', 5), ('Cusco', 'Arequipa', 3),
        ('Lima', 'Trujillo', 10), ('Trujillo', 'Piura', 4),
        ('Arequipa', 'Piura', 6), ('Cusco', 'Ica', 2),
        ('Ica', 'Arequipa', 2), ('Arequipa', 'Tacna', 5),
        ('Tacna', 'Puno', 3), ('Puno', 'Huancayo', 8),
        ('Huancayo', 'Cajamarca', 2), ('Cajamarca', 'Ayacucho', 6),
        ('Ayacucho', 'Chiclayo', 4), ('Chiclayo', 'Tacna', 5),
        ('Chiclayo', 'Huancayo', 7), ('Lima', 'Moquegua', 12),
        ('Moquegua', 'Trujillo', 5), ('Tumbes', 'Cusco', 6),
        ('Tarapoto', 'Arequipa', 8)
    ]
    
    for conn in connections:
        graph.add_edge(conn[0], conn[1], conn[2])

    start_node = 'Lima'
    goal_node = 'Huancayo'

    running = True
    traffic_update_counter = 0  
    dragging_node = None
    while running:
        screen.fill(WHITE)

        graph.draw(screen)

        #traffic_update_counter += 1
        #if traffic_update_counter % 10 == 0:
        #   simulate_traffic(graph)

        path = a_star_search(graph, start_node, goal_node)

        if path:
            for i in range(len(path) - 1):
                from_pos = graph.get_node_pos(path[i])
                to_pos = graph.get_node_pos(path[i+1])
                pygame.draw.line(screen, PATH_COLOR, from_pos, to_pos, 5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    for node in graph.nodes:
                        if node.is_mouse_over(event.pos):
                            dragging_node = node
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_node = None
            
            if event.type == pygame.MOUSEMOTION:
                if dragging_node:
                    dragging_node.x, dragging_node.y = event.pos

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
