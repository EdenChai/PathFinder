from flask import Flask, request, jsonify, render_template
import json
import networkx as nx
from fastkml import kml
from flask_cors import CORS
from haversine import haversine, Unit
from shapely.geometry import LineString, Point
from scipy import spatial

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Constants
GRAPH_FILE = 'graph_example.json'

# Global flag to track initialization
initialized = False

@app.before_request
def initialize():
	"""
	The function effectively implements the Singleton design pattern.
	Initialize the graph and KD-Tree before handling the first request.
	This ensures that resources are loaded once and available for all subsequent requests.
	"""
	global initialized
	if not initialized:
		graph_data = load_json_file(GRAPH_FILE)
		app.config['graph'] = create_graph(graph_data)
		app.config['kd_tree'] = create_kd_tree()
		initialized = True

def load_json_file(file_name):
	"""
	Load the graph data from a JSON file.

	:param file_name: The name of the file to load.
	:return: The graph data as a dictionary.
	"""
	with open(file_name, 'r') as f:
		graph_data = json.load(f)
		return graph_data

def create_graph(graph_data):
	"""
		Build a graph using NetworkX from the provided data.
		Using NetworkX is useful for making complex calculations.

	    :param graph_data: Dictionary of graph data where keys are nodes and values are their neighbors.
	    :return: A NetworkX graph object.
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
    Calculate the distance between two points using the Haversine formula.
	The haversine formula determines the great-circle distance between
	two points on a sphere given their longitudes and latitudes.

    :param p1: Tuple representing the first point (latitude, longitude).
    :param p2: Tuple representing the second point (latitude, longitude).
    :return: The distance between the two points in meters.
	"""
	return haversine(p1, p2, unit=Unit.METERS)

def create_kd_tree():
	"""
		Create a KD-Tree from the graph nodes for efficient nearest neighbor search.
		Time Complexity: O(N*log(N)) for building the tree.
		Space Complexity: O(N)

		:return: A KD-Tree object.
	"""
	G = app.config['graph']
	kd_tree = spatial.KDTree(G.nodes())
	return kd_tree

def find_closest_point(point):
	"""
	    Find the closest point in the graph to the given point using a KD-Tree.
		Time Complexity: O(logN)

		:param point: The point for which to find the closest point.
		:return: The closest point in the graph.
	"""
	G = app.config['graph']
	kd_tree = app.config['kd_tree']
	node_list = list(G.nodes())
	index = kd_tree.query(point)[1]
	closest_point = node_list[index]
	return closest_point

def find_shortest_path(start_point, end_point):
	"""
	    Find the shortest path between two points in the graph using Dijkstra's algorithm.
		Time Complexity: O((V+E)*log(V)) - it's using with a priority queue.

	    :param start_point: The starting point as a tuple (latitude, longitude).
	    :param end_point: The ending point as a tuple (latitude, longitude).
	    :return: A list representing the shortest path, or None if no path exists.
	"""
	G = app.config['graph']
	try:
		shortest_path = nx.dijkstra_path(G, source=start_point, target=end_point, weight="weight")
		return shortest_path
	except nx.NetworkXNoPath:
		return None

def generate_kml_file(shortest_path):
	"""
	    Generate a KML file representing the shortest path.

		:param shortest_path: A list of coordinates representing the shortest path.
        :return: A string containing the KML file content.
	"""
	k = kml.KML()
	namespace = '{http://www.opengis.net/kml/2.2}'
	doc = kml.Document(ns=namespace, id='doc_id', name='Shortest Path')
	k.append(doc)

	# Correct the order to (longitude, latitude)
	corrected_path = [(lon, lat) for lat, lon in shortest_path]

	# Create placemarks for each point in the path
	for index, (lon, lat) in enumerate(corrected_path):
		point = Point(lon, lat)
		point_placemark = kml.Placemark(ns=namespace, id=f'point_{index}', name=f'Point {index + 1}')
		point_placemark.geometry = point
		doc.append(point_placemark)

	# Create a linestring for the shortest path
	line = LineString(corrected_path)
	path_placemark = kml.Placemark(ns=namespace, id='path', name='Shortest Path')
	path_placemark.geometry = line
	doc.append(path_placemark)

	# Return the KML content as a string
	return k.to_string(prettyprint=True)

@app.route('/', methods=['GET'])
def render_page():
	"""
	    Handle the GET request to render the HTML page.
		:return: The rendered HTML page.
	"""
	return render_template('index.html')

@app.route('/', methods=['POST'])
def find_path():
	"""
	    Handle the POST request to find the shortest path between two points.
	    :return: A JSON response with the shortest path and KML content, or an error message.
	"""
	try:
		# Extract start and end coordinates from the incoming JSON request
		start_lat = float(request.json['start']['lat'])
		start_lon = float(request.json['start']['lon'])
		end_lat = float(request.json['end']['lat'])
		end_lon = float(request.json['end']['lon'])

		# Validate the input coordinates
		if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
			return jsonify({ 'error': 'Invalid start point input! Please enter valid coordinates.' }), 400
		if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
			return jsonify({ 'error': 'Invalid end point input! Please enter valid coordinates.' }), 400

		# Convert the coordinates to tuples
		start_point = (start_lat, start_lon)
		end_point = (end_lat, end_lon)

		if start_point == end_point:
			return jsonify({'error': 'Start and end points cannot be the same'}), 404

		# Find the closest points in the graph
		start_closest = find_closest_point(start_point)
		end_closest = find_closest_point(end_point)

		if start_closest == end_closest:
			return jsonify({'error': 'Start and end points are too close; please provide more distant points'}), 404

		# Find the shortest path between the closest points
		shortest_path = find_shortest_path(start_closest, end_closest)

		if shortest_path:
			kml_content = generate_kml_file(shortest_path)
			return jsonify({ 'shortest_path': shortest_path, 'kml_content': kml_content }), 200
		else:
			return jsonify({ 'error': 'No path found between the provided points.' }), 404

	except KeyError as e:
		return jsonify({ 'error': f'Missing data {str(e)}' }), 400


if __name__ == '__main__':
	app.run(debug=True)