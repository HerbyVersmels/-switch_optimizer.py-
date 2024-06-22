from PIL import Image
import pytesseract
import re
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# OCR Function
def extract_text(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

# Parsing Function
def parse_switch_list(text):
    cars = []
    for line in text.split('\n'):
        match = re.match(r'(\d+)\s+(\w+)\s+(\d+)\s+(\w+)', line)
        if match:
            cars.append({
                'number': match.group(1),
                'type': match.group(2),
                'weight': match.group(3),
                'destination': match.group(4)
            })
    return cars

# Optimization Function
def create_data_model(cars):
    data = {}
    data['distances'] = [...]  # Add actual distance data here
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data

def optimize_switching(cars):
    data = create_data_model(cars)
    manager = pywrapcp.RoutingIndexManager(len(data['distances']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distances'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        return print_solution(data, manager, routing, solution)

def print_solution(data, manager, routing, solution):
    plan_output = 'Switching Plan:\n'
    index = routing.Start(0)
    while not routing.IsEnd(index):
        plan_output += f' {manager.IndexToNode(index)} ->'
        index = solution.Value(routing.NextVar(index))
    plan_output += f' {manager.IndexToNode(index)}\n'
    return plan_output

# Main Execution
text = extract_text('switch_list.jpg')  # Ensure this path is correct on your iPhone
cars = parse_switch_list(text)
instructions = optimize_switching(cars)
print(instructions)
