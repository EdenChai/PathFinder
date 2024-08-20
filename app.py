from flask import Flask, request, jsonify, render_template
import json
import networkx as nx
from fastkml import kml
from flask_cors import CORS
from haversine import haversine, Unit
from shapely.geometry import LineString

app = Flask(__name__)
CORS(app, supports_credentials=True)

"""
	The function loads the data from the JSON file
"""
def load_json_file(file_name):
	with open(file_name, 'r') as f:
		graph_data = json.load(f)
		return graph_data

"""
	I chose to use networkX to build the predefined graph.
	In this way, we can do complex calculations
	such as calculating distances between vertices 
	and finding the shortest path in the graph.
"""
def create_predefined_graph(graph_data):
	G = nx.Graph()
	for node, neighbors in graph_data.items():
		node = tuple(map(float, node.strip('()').split(', ')))
		G.add_node(node)
		for neighbor in neighbors:
			neighbor = tuple(neighbor)
			G.add_node(neighbor)
			G.add_edge(node, neighbor, weight=calculate_distance(node, neighbor))
	return G

"""
	This function calculates the distance between two neighbor nodes.
	I used Haversine formula because it has O(1) time complexity.
"""
def calculate_distance(p1, p2):
	return haversine(p1, p2, unit=Unit.METERS)

"""
	Complexity O(n * m) where n is the number of vertices and m is the number of queries.
	Since the problem requires only m=2 queries, the running time will be linear.
	Alternative - using a "K-D Tree" requires O(n*logn) runtime and O(n) space.
"""
def find_closest_point(G, point):
	min_distance = float('inf')
	closest_point = None
	for node in G.nodes():
		distance = calculate_distance(point, node)
		if distance < min_distance:
			min_distance = distance
			closest_point = node
	return closest_point

"""
	The function calculate the shortest distance and returns the shortest path.
	I used Dijkstra algorithm to find the shortest path.
	Dijkstra algorithm is optimal for finding the shortest path in graphs with non-negative edge weights.
	Time Complexity: O(V^2) 
"""
def find_shortest_path(G, start_point, end_point):
	try:
		shortest_path = nx.dijkstra_path(G, source=start_point, target=end_point, weight="weight")
		return shortest_path
	except nx.NetworkXNoPath:
		return None

@app.route('/', methods=['POST'])
def find_path():

	# Need to load html file
	if request.method == 'GET':
		return render_template('index.html')

	try:
		# Load graph data and create graph object (assumes you have these functions implemented)
		graph_data = load_json_file('graph_example.json')
		G = create_predefined_graph(graph_data)

		# Extract start and end coordinates from the incoming JSON request
		start_lat = float(request.json['start']['lat'])
		start_lon = float(request.json['start']['lon'])
		end_lat = float(request.json['end']['lat'])
		end_lon = float(request.json['end']['lon'])

		# Define start and end points as tuples
		start_point = (start_lat, start_lon)
		end_point = (end_lat, end_lon)

		# Find the closest points in the graph
		start_closest = find_closest_point(G, start_point)
		end_closest = find_closest_point(G, end_point)

		# Calculate the shortest path
		shortest_path = find_shortest_path(G, start_closest, end_closest)

		kml_content = generate_KML_file(shortest_path)
		# plot_file = plot_graph_with_shortest_path(G, shortest_path)

		if shortest_path is not None:
			return jsonify({
				'shortest_path': shortest_path,
				'kml_content': kml_content
			}), 200
		else:
			return jsonify({ 'error': 'No path found between the provided points.' }), 404

	except KeyError as e:
		return jsonify({ 'error': f'Missing data {str(e)}' }), 400

	except ValueError:
		return jsonify({ 'error': 'Invalid input! Please enter valid coordinates.' }), 400

def generate_KML_file(shortest_path):
	# Create a aKML object
	k = kml.KML()

	# KML namespace
	ns = '{http://www.opengis.net/kml/2.2}'
	# Create a document
	doc = kml.Document(ns, 'doc_id', 'Shortest Path')
	k.append(doc)

	# Correct the order to (longitude, latitude)
	corrected_path = [(lon, lat) for lat, lon in shortest_path]

	# Create a linestring for the shortest path
	line = LineString(corrected_path)

	placemark = kml.Placemark(ns, 'id', 'Shortest Path')
	placemark.geometry = line
	doc.append(placemark)

	# Return the KML content as a string
	return k.to_string(prettyprint=True)

# todo: Create a plot of the graph with basemap of Israel, and highlight the shortest path.
def plot_graph_with_shortest_path(G, shortest_path):
	pass

if __name__ == '__main__':
	app.run(debug=False)