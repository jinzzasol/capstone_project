import React, { useState } from 'react';
import '../css/SuggestionsTab.css';
import axios from 'axios';

function SuggestionsTab({ suggestions = [], onClose = () => {}, isLoading = false }) {
    // State to manage loading status of feedback submission for each suggestion
    const [loadingFeedback, setLoadingFeedback] = useState({});
    const [feedbackStatus, setFeedbackStatus] = useState({});
    const [isVisible, setIsVisible] = useState(true);

    const handleFeedback = async (id, feedback) => {
        setLoadingFeedback({ ...loadingFeedback, [id]: true });
        setFeedbackStatus({ ...feedbackStatus, [id]: { loading: true } }); 

        try {
            const response = await axios.post('http://52.91.5.78:7070/api/suggestions/feedback', { id, feedback });
            console.log(`Feedback sent for suggestion ${id}: ${feedback}`);
            setFeedbackStatus({
                ...feedbackStatus,
                [id]: { loading: false, message: response.data.message },
            });
        } catch (error) {
            console.error("Error sending feedback:", error);
            setFeedbackStatus({
                ...feedbackStatus,
                [id]: { loading: false, message: "Error sending feedback" },
            });
        } finally {
            setLoadingFeedback({ ...loadingFeedback, [id]: false });
        }
    };

    const handleClose = () => {
        setIsVisible(false);
        onClose();
    };

    if (!Array.isArray(suggestions)) {
        return null;
    }

    return (
        <div className={`suggestions-container ${!isVisible ? 'hide' : ''}`}>
            <button className="close-btn" onClick={handleClose}>Close</button>
            <div className="suggestions-content">
                {isLoading ? (
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>Analyzing your code...</p>
                    </div>
                ) : (
                    suggestions.map((suggestion) => (
                        <div key={suggestion?.id || Math.random()} className="suggestion-item">
                            <div className="suggestion-text">
                                {suggestion?.text || ''}
                            </div>
                            <div className="feedback-buttons">
                                {feedbackStatus[suggestion?.id]?.loading ? (
                                    <div>Loading...</div>
                                ) : feedbackStatus[suggestion?.id]?.message ? (
                                    <div>{feedbackStatus[suggestion?.id].message}</div>
                                ) : (
                                    <>
                                        <button onClick={() => handleFeedback(suggestion?.id, 'like')}>👍 Like</button>
                                        <button onClick={() => handleFeedback(suggestion?.id, 'dislike')}>👎 Dislike</button>
                                    </>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default SuggestionsTab;
