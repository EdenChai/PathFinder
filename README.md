
# PathFinder

## Project Overview
PathFinder is a web application that processes geographical coordinate inputs, finds the closest points within a predefined graph, computes the shortest path between these points, and returns the path to the client.
The application also provides an option to generate a KML file representing the path.

## Features
- Calculate the shortest path between two geographical coordinates.
- Find the closest points within a predefined graph.
- Generate a KML file representing the path.
- Simple web interface for entering coordinates.

## Instructions

### 1. Clone the Repository
To get started, first clone the repository to your local machine:
```bash
git clone https://github.com/edenchai/PathFinder.git
cd PathFinder
```

### 2. Install Required Packages

1. **Create a virtual environment**:
     ```bash
     python -m venv venv
     ```
     
2. **Activate the virtual environment**:
     ```bash
     .\.venv\Scripts\activate
     ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Run the Application
To run the application locally, use the following command:

```bash
flask run
```

This will start the Flask development server, and the application will be accessible at `http://127.0.0.1:5000/`.

### 4. Using the Application

#### Web Interface
1. **Access the Application**:
   - Open your web browser and navigate to `http://127.0.0.1:5000/`.
   - You will see a simple web form where you can enter the start and end coordinates.

2. **Enter Coordinates**:
   - Input the start and end latitude and longitude values in the respective fields.
   - Click the "Find Path" button to submit the form.

3. **View Results**:
   - If the path is successfully calculated, the shortest path will be displayed, along with an option to download the corresponding KML file.
   - If an error occurs, a message will be displayed.

#### API Usage
The application also provides an API endpoint that can be accessed programmatically.

- **Endpoint**: `POST /`
- **Request Format**: JSON
  ```json
  {
    "start": {"lat": 32.0853, "lon": 34.7818},
    "end": {"lat": 31.7683, "lon": 35.2137}
  }
  ```
- **Response Format**: JSON
  ```json
  {
    "shortest_path": [[lat1, lon1], [lat2, lon2], ...],
    "kml_content": "KML content here..."
  }
  ```

### 5. How to Upload KML File to Google Earth
1. **Download the KML file** from the application.
2. **Open Google Earth** (either the web or desktop version).
3. **Upload the KML file**:
   - **In Google Earth Web**:
     - Click on "Projects" in the left sidebar.
     - Click on "New Project" -> "Import KML file from computer".
     - Select your downloaded KML file and upload it.

4. **View the Path**: The path will be displayed on the map.
