/* suggestionstab.js */
import React from 'react';
import '../css/SuggestionsTab.css';
function SuggestionsTab({ suggestions, onClose }) {
    return (
      <div className="suggestions-container">
        <button className="close-btn" onClick={onClose}>Close</button>
        <div className="suggestions-content">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="suggestion-item">
              <pre><code>{suggestion}</code></pre>
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  
  export default SuggestionsTab;
  