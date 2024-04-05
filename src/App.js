import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import HeaderApp from './components/HeaderApp'; 
import DescriptionBox from './components/DescriptionBox';
import CodeEditor from './components/CodeEditor';
import CodeTabs from './components/CodeTabs';
import questions from './data/questions';
import SuggestionsTab from './components/SuggestionsTab'
import { sendCodeToBackend } from './lib/codeHandler'

function App() {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [activeLanguage, setActiveLanguage] = useState('python');
  // Assume initial code is based on the first question
  const [code, setCode] = useState('');

  // Adding state to hold question details fetched from the API
  const [questionDetails, setQuestionDetails] = useState({ title: '', description: '' });
  const [isSuggestionsVisible, setSuggestionsVisible] = useState(false);
    
  // Toggle visibility based on your application logic
  const toggleSuggestions = () => setSuggestionsVisible(!isSuggestionsVisible);


  // Function to fetch question details
  const fetchQuestionDetails = async () => {
    try {
      // Update the URL according to your API endpoint structure
      const response = await axios.get(`http://localhost:7070/api/questions/${currentQuestionIndex}`);
      setQuestionDetails({
        title: response.data.title,
        description: response.data.description
      });
      // Assuming the API also returns a starter code snippet for the question
      setCode(response.data.starterCode || '');
    } catch (error) {
      console.error('There was an error fetching question details:', error);
    }
  };

  // Effect to fetch question details whenever the currentQuestionIndex changes
  useEffect(() => {
    fetchQuestionDetails();
  }, [currentQuestionIndex]);

  const handlePreviousClick = () => {
    setCurrentQuestionIndex((prevIndex) => Math.max(prevIndex - 1, 0));
  };
  const handleNextClick = () => {
    setCurrentQuestionIndex((prevIndex) => Math.min(prevIndex + 1, questions.length - 1));
  };

  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const sampleSuggestion = [
    { id: 1, text: "Here's a suggestion to improve your code!", feedback: null },
  ];
  



  const generateRandomSubmissionId = () => {
    const timestamp = Date.now(); 
    const randomPortion = Math.random().toString(36).substring(2, 15);
    return `submission-${timestamp}-${randomPortion}`;
  };
  
  const handleSubmit = async () => {
    const questionId = questions[currentQuestionIndex].id;
    const submissionId = generateRandomSubmissionId();
    const submissionUrl = 'http://localhost:7070/api/submit-code'; // Your Flask backend endpoint for code submission

    console.log("Submitting Code:", code, "Question ID:", questionId, "Submission ID:", submissionId);

    try {
      // Prepare the submission data
      const submissionData = {
        code: code,
        questionId: questionId,
        submissionId: submissionId
      };

      // Send the submission data to the backend
      const response = await axios.post(submissionUrl, submissionData);
      console.log("Backend Response:", response.data);

      // Assume the backend response contains suggestions in `response.data.suggestions`
      setSuggestions(response.data.suggestions); // Use actual suggestions from the backend
      setShowSuggestions(true);
    } catch (error) {
      console.error("Error from backend:", error);
      setSuggestions([{
        id: 0,
        text: "There was an error processing your request. Please try again later.",
        feedback: null
      }]);
      setShowSuggestions(true); // Optionally, you might want to still show the suggestions box with the error message
    }
  };

  const handleCloseSuggestions = () => {
    setShowSuggestions(false); 
  };

  
  return (
    <div className="App">
      <HeaderApp />
      <div className="content">
      <div className="description-box-container" style={{flex: isSuggestionsVisible ? '0.5' : '1'}}>
          <DescriptionBox
            title={questionDetails.title}
            description={questionDetails.description}
            onPreviousClick={handlePreviousClick}
            onNextClick={handleNextClick}
            isFirst={currentQuestionIndex === 0}
            isLast={currentQuestionIndex === questions.length - 1}
          />
        </div>
        <div className="right-container">
          <CodeTabs activeLanguage={activeLanguage} setActiveLanguage={setActiveLanguage} />
          <div className="main-container">
            <div className="code-editor-container" style={{flex: isSuggestionsVisible ? '0.5' : '1'}}>
            <CodeEditor language={activeLanguage} code={code} setCode={setCode} />
          </div> 
          </div>
  {showSuggestions && (
    <div className="lower-container">
      <SuggestionsTab suggestions={suggestions} onClose={handleCloseSuggestions} />
    </div>
  )}
  <button 
    className="submit-button" 
    onClick={handleSubmit}
    style={{ position: 'absolute', right: '20px', bottom: '175px', padding: '10px 20px' }}
  >
    Submit
  </button>
        </div>
      </div>
    </div>
  );
}
export default App;
