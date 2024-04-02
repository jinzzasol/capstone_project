/* suggestionstab.js */
import React from 'react';
import '../css/SuggestionsTab.css';
import axios from 'axios';

function SuggestionsTab({ suggestions, onClose }) {
    console.log(suggestions);

    const handleFeedback = async (id, feedback) => {
        try {
          await axios.post('/api/suggestions/feedback', { id, feedback });
          console.log(`Feedback sent for suggestion ${id}: ${feedback}`);
        } catch (error) {
          console.error("Error sending feedback:", error);
        }
      };
      
  
    return (
      <div className="suggestions-container">
        <button className="close-btn" onClick={onClose}>Close</button>
        <div className="suggestions-content">
          {suggestions.map((suggestion) => (
            <div key={suggestion.id} className="suggestion-item">
              <pre><code>{suggestion.text}</code></pre>
              <div className="feedback-buttons">
                <button onClick={() => handleFeedback(suggestion.id, 'like')}>👍 Like</button>
                <button onClick={() => handleFeedback(suggestion.id, 'dislike')}>👎 Dislike</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  
  
  export default SuggestionsTab;
  