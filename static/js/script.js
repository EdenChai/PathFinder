document.getElementById('path-form').addEventListener('submit', async function (event)
{
    // Preventing page reload
    event.preventDefault();

    // Get the values from the form fields
    const startLat = document.getElementById('start-lat').value;
    const startLon = document.getElementById('start-lon').value;
    const endLat = document.getElementById('end-lat').value;
    const endLon = document.getElementById('end-lon').value;

    // Prepare the request payload
    const payload = {
        start: {lat: startLat, lon: startLon},
        end: {lat: endLat, lon: endLon}
    };

    try
    {
        // Send the coordinates to the server in the expected format
        const response = await fetch('http://127.0.0.1:5000/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        // Get the JSON response
        const result = await response.json();

        // Ensure the result container is displayed
        const resultContainer = document.getElementById('result-container');
        resultContainer.style.display = 'block';

        if (response.status !== 200)
        {
            // Display the error message
            displayError(result.error);
            return;
        }

        // Display the result
        displayResult(result);
    }

    catch (error)
    {
        console.error('Error:', error);
        displayError('An error occurred while finding the path.');
    }
});

function displayResult(result)
{
    const resultElement = document.getElementById('result');

        resultElement.innerHTML = `
            <div class="result-block">
                <p class="shortest-path">Shortest Path: ${JSON.stringify(result.shortest_path)}</p>
                <a id="download-link" class="btn btn-success btn-download" download="shortest_path.kml">Download KML File</a>
            </div>
        `;
        setDownloadLink(result.kml_content);
}

function displayError(errorMessage)
{
    document.getElementById('result').innerHTML = `
        <div class="result-block">
            <p class="shortest-path text-danger">${errorMessage}</p>
        </div>
        `;
}

function setDownloadLink(kmlContent)
{
    const blob = new Blob([kmlContent], {type: 'application/vnd.google-earth.kml+xml'});
    const url = URL.createObjectURL(blob);
    const downloadLink = document.getElementById('download-link');
    downloadLink.href = url;
}