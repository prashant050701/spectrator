import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SearchPage from './SearchPage';  // Updated import path
import SpectraDisplay from './SpectraDisplay';  // Updated import path
import './index.css';

function App() {
  return (
    <Router>
      <div className="container">
        <Routes>
          <Route path="/" element={<SearchPage />} exact />
          <Route path="/spectra/:name" element={<SpectraDisplay />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
