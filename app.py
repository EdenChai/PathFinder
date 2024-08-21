from flask import Flask, request, jsonify, render_template
import json
import networkx as nx
from fastkml import kml
from flask_cors import CORS
from haversine import haversine, Unit
from shapely.geometry import LineString

app = Flask(__name__)
CORS(app, supports_credentials=True)

def load_json_file(file_name):
	"""
		The function loads the data from the JSON file
	"""
	with open(file_name, 'r') as f:
		graph_data = json.load(f)
		return graph_data

def create_predefined_graph(graph_data):
	"""
		I chose to use networkX to build the predefined graph.
		In this way, we can do complex calculations.
	"""
	G = nx.Graph()
	for node, neighbors in graph_data.items():
		node = tuple(map(float, node.strip('()').split(', ')))
		G.add_node(node)
		for neighbor in neighbors:
			neighbor = tuple(neighbor)
			G.add_node(neighbor)
			G.add_edge(node, neighbor, weight=calculate_distance(node, neighbor))
	return G

def calculate_distance(p1, p2):
	"""
		This function calculates the distance between two neighbor nodes.
		I used Haversine formula because it has O(1) time complexity.
	"""
	return haversine(p1, p2, unit=Unit.METERS)

def find_closest_point(G, point):
	"""
		Complexity O(n * m) where n is the number of vertices and m is the number of queries.
		Since the problem requires only m=2 queries, the running time will be linear.
		Alternative - using a "K-D Tree" requires O(n*logn) runtime and O(n) space.
	"""
	min_distance = float('inf')
	closest_point = None
	for node in G.nodes():
		distance = calculate_distance(point, node)
		if distance < min_distance:
			min_distance = distance
			closest_point = node
	return closest_point

def find_shortest_path(G, start_point, end_point):
	"""
		The function calculate the shortest distance and returns the shortest path.
		I used Dijkstra algorithm to find the shortest path.
		Dijkstra algorithm is optimal for finding the shortest path in graphs with non-negative edge weights.
		Time Complexity: O(V^2)
	"""
	try:
		shortest_path = nx.dijkstra_path(G, source=start_point, target=end_point, weight="weight")
		return shortest_path
	except nx.NetworkXNoPath:
		return None

def generate_KML_file(shortest_path):
	"""
		This function generates a KML file representing the shortest path.
		:param shortest_path: A list of coordinates representing the shortest path.
        :return: A string containing the KML file content.
	"""

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

	placemark = kml.Placemark(ns=ns, name="Shortest Path")
	placemark.geometry = line
	doc.append(placemark)

	# Return the KML content as a string
	return k.to_string(prettyprint=True)

@app.route('/', methods=['GET', 'POST'])
def find_path():
	"""
	    This endpoint handles both GET and POST requests.
	    For POST requests, it calculates the shortest path between two point and returns the path and KML content.
	    For GET requests, it renders the index.html page.
	    :return: JSON response with the shortest path and KML content, or an HTML page.
	"""

	# Need for loading the HTML page
	if request.method == 'POST':

		try:
			# Load graph data from JSON file
			graph_data = load_json_file('graph_example.json')

			# Create the predefined graph
			G = create_predefined_graph(graph_data)

			# Extract start and end coordinates from the incoming JSON request
			start_lat = float(request.json['start']['lat'])
			start_lon = float(request.json['start']['lon'])
			end_lat = float(request.json['end']['lat'])
			end_lon = float(request.json['end']['lon'])

			# Validate the input coordinates
			if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
				raise ValueError("Invalid start coordinates")
			if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
				raise ValueError("Invalid end coordinates")

			# Define start and end points as tuples
			start_point = (start_lat, start_lon)
			end_point = (end_lat, end_lon)

			if start_point == end_point:
				return jsonify({'error': 'Do not enter the same coordinates of the start and end points'}), 404

			# Find the closest points in the graph
			start_closest = find_closest_point(G, start_point)
			end_closest = find_closest_point(G, end_point)

			if start_closest == end_closest:
				return jsonify({'error': 'The closest start and end points have the same coordinates. Try entering more distant points.'}), 404

			# Calculate the shortest path
			shortest_path = find_shortest_path(G, start_closest, end_closest)

			if shortest_path is not None:
				# Generate KML file
				kml_content = generate_KML_file(shortest_path)

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

	else:
		return render_template('index.html')


if __name__ == '__main__':
	app.run(debug=False)