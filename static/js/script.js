document.getElementById('path-form').addEventListener('submit',
    async function (event) {
        event.preventDefault();

        // Get the values from the form fields
        const startLat = document.getElementById('start-lat').value;
        const startLon = document.getElementById('start-lon').value;
        const endLat = document.getElementById('end-lat').value;
        const endLon = document.getElementById('end-lon').value;

        try {
            // Send the coordinates to the server in the expected format
            const response = await fetch('http://127.0.0.1:5000/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    start: {lat: startLat, lon: startLon},
                    end: {lat: endLat, lon: endLon}
                })
            });

            // Get the JSON response
            const result = await response.json();

            // Ensure the result container is displayed
            document.getElementById('result-container').style.display = 'block';

            if (!response.ok) {
                document.getElementById('result').innerHTML = `
                        <div class="result-block">
<!--                            <h3>Result</h3>-->
                            <p class="shortest-path text-danger">${result.error}</p>
                        </div>
                        `;
            } else if (result.shortest_path) {
                document.getElementById('result').innerHTML = `
                <div class="result-block">
                    <p class="shortest-path">Shortest Path: ${JSON.stringify(result.shortest_path)}</p>
                    <a id="download-link" class="btn btn-success btn-download" download="shortest_path.kml">Download KML File</a>
                </div>
            `;

                // Create a Blob from the KML content and set the download link
                const blob = new Blob([result.kml_content], {type: 'application/vnd.google-earth.kml'});
                const url = URL.createObjectURL(blob);
                document.getElementById('download-link').href = url;
            } else {
                document.getElementById('result').textContent = 'Error: ' + result.error;
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('result').textContent = 'An error occurred while finding the path.';
        }
    });