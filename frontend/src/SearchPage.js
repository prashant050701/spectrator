import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function SearchPage() {
  const [name, setName] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const navigate = useNavigate();

  const search = (e) => {
    e.preventDefault();
    navigate(`/spectra/${name}`);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div>
        <h1 style={{ textAlign: 'center' }}>Spectrator</h1>
        <form onSubmit={search} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter star name"
            required
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            style={{
              marginBottom: '10px',
              padding: '10px',
              width: '300px',
              border: '1px solid #ccc',
              borderRadius: '5px',
              backgroundImage: `url('/strip.png')`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundColor: 'white',
              backgroundBlendMode: isFocused ? 'saturation' : 'none',
              transition: 'background 0.5s ease',
            }}
          />
          <button type="submit" style={{ padding: '10px 20px' }}>Search</button>
        </form>
      </div>
    </div>
  );
}

export default SearchPage;
