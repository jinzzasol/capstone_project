import React, { useState } from 'react';
import '../css/SuggestionsTab.css';
import axios from 'axios';

function SuggestionsTab({ suggestions, onClose }) {
    // State to manage loading status of feedback submission for each suggestion
    const [loadingFeedback, setLoadingFeedback] = useState({});

    const [feedbackStatus, setFeedbackStatus] = useState({});
    const handleFeedback = async (id, feedback) => {
        setLoadingFeedback({ ...loadingFeedback, [id]: true }); // Start loading for this id
        setFeedbackStatus({ ...feedbackStatus, [id]: { loading: true } }); 

        try {
          const response = await axios.post('http://localhost:7070/api/suggestions/feedback', { id, feedback });
          console.log(`Feedback sent for suggestion ${id}: ${feedback}`);
          setFeedbackStatus({
            ...feedbackStatus,
            [id]: { loading: false, message: response.data.message },
          });
        } catch (error) {
          console.error("Error sending feedback:", error);
        } finally {
          setLoadingFeedback({ ...loadingFeedback, [id]: false }); // Stop loading for this id
        }
      };
      const [isVisible, setIsVisible] = useState(true); // Manage visibility
  
      const handleClose = () => {
          setIsVisible(false); // Hide the tab
          onClose(); // Call the onClose prop function if needed
      };
    return (
<div className={`suggestions-container ${!isVisible ? 'hide' : ''}`}>
        <button className="close-btn" onClick={handleClose}>Close</button>
        <div className="suggestions-content">
          {suggestions.map((suggestion) => (
            <div key={suggestion.id} className="suggestion-item">
              <pre><code>{suggestion.text}</code></pre>
              <div className="feedback-buttons">
                {feedbackStatus[suggestion.id]?.loading ? (
                  <div>Loading...</div>
                ) : feedbackStatus[suggestion.id]?.message ? (
                  <div>{feedbackStatus[suggestion.id].message}</div> // Show response message
                ) : (
                  <>
                    <button onClick={() => handleFeedback(suggestion.id, 'like')}>👍 Like</button>
                    <button onClick={() => handleFeedback(suggestion.id, 'dislike')}>👎 Dislike</button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
}

export default SuggestionsTab;
