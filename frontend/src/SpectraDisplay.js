import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import Plot from 'react-plotly.js';

function SpectraDisplay() {
  const { name } = useParams();
  const [plots, setPlots] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true; // Flag to prevent state updates after unmount
    setLoading(true);
    setError('');
    setPlots([]);

    let surveysData = null;

    axios.get('/surveys.json')
      .then(surveyRes => {
        surveysData = surveyRes.data;
        return axios.post('http://127.0.0.1:5000/get_spectrum', { name }, {
          headers: { 'Content-Type': 'application/json' }
        });
      })
      .then(response => {
        const spectra = response.data.spectra || [];
        if (spectra.length > 0) {
          const fetchPromises = [];
          const plotsArray = [];

          spectra.forEach((spectrum, spectrumIndex) => {
            const { file_path, source_type, filter_name } = spectrum;
            const surveyInfo = surveysData[source_type];

            if (!surveyInfo) {
              console.error(`Survey information not found for source type: ${source_type}`);
              setError(`Survey information not found for source type: ${source_type}`);
              return;
            }

            fetchPromises.push(
              axios.get(file_path)
                .then(csvRes => {
                  const data = processCsvData(csvRes.data, surveyInfo.columns);

                  plotsArray.push({
                    data: data,
                    title: `${surveyInfo.source}${filter_name ? ' - ' + filter_name : ''}`,
                    unit: surveyInfo.units,
                    index: spectrumIndex
                  });
                })
                .catch(error => {
                  console.error('Error fetching CSV data:', error);
                  setError('Error fetching CSV data: ' + error.message);
                })
            );
          });

          Promise.all(fetchPromises)
            .then(() => {
              // Sort plotsArray based on the index to preserve order
              plotsArray.sort((a, b) => a.index - b.index);
              const sortedPlots = plotsArray.map(item => ({
                data: item.data,
                title: item.title,
                unit: item.unit
              }));
              if (isMounted) {
                setPlots(sortedPlots);
                setLoading(false);
              }
            })
            .catch(err => {
              console.error('Error fetching spectra:', err);
              setError('Failed to fetch spectra: ' + err.message);
              setLoading(false);
            });
        } else {
          setError("No spectra available for the given identifier");
          setLoading(false);
        }
      })
      .catch(error => {
        console.error('Error fetching spectra:', error);
        setError('Failed to fetch spectra: ' + (error.response?.data.error || error.message || 'Network error'));
        setLoading(false);
      });

    return () => {
      isMounted = false; // Clean up flag on unmount
    };
  }, [name]);

  function processCsvData(csvData, columns) {
    const rows = csvData.trim().split('\n');
    const wavelength = [];
    const flux = [];

    // Map the columns based on the provided column names
    const columnNames = rows[0].split(',');
    const wavelengthIndex = columnNames.indexOf(columns.wavelength);
    const fluxIndex = columnNames.indexOf(columns.flux);

    for (let i = 1; i < rows.length; i++) {
      const cols = rows[i].split(',');
      if (cols.length >= 2) {
        wavelength.push(parseFloat(cols[wavelengthIndex]));
        flux.push(parseFloat(cols[fluxIndex]));
      }
    }

    return { x: wavelength, y: flux, type: 'scatter', mode: 'lines', name: 'Flux', line: { color: '#007bff' } };
  }

  return (
    <div className="d-flex flex-column vh-100">
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <Link className="navbar-brand" to="/">
          <img src="/logo_spectrator.png" height="30" alt="Spectrator" />
        </Link>
        <div className="navbar-nav ml-auto">
          <Link className="nav-item nav-link" to="/">Search Spectra</Link>
        </div>
      </nav>
      <div className="container flex-grow-1 d-flex flex-column align-items-center justify-content-center">
        <h1 className="text-center">Spectra for {name}</h1>
        {loading ? (
          <p className="text-center">Loading...</p>
        ) : plots.length > 0 ? (
          plots.map((plot, index) => (
            <Plot
              key={index}
              data={[plot.data]}
              layout={{
                title: plot.title,
                xaxis: { title: `Wavelength (${plot.unit})` },
                yaxis: { title: 'Flux' },
                showlegend: false
              }}
              style={{ width: "100%", height: "400px" }}
            />
          ))
        ) : (
          <p className="text-center">{error}</p>
        )}
      </div>
    </div>
  );
}

export default SpectraDisplay;
