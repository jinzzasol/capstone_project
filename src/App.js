import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import HeaderApp from './components/HeaderApp'; 
import DescriptionBox from './components/DescriptionBox';
import CodeEditor from './components/CodeEditor';
import CodeTabs from './components/CodeTabs';
import questions from './data/questions';

function App() {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [activeLanguage, setActiveLanguage] = useState('python');
  // Assume initial code is based on the first question
  const [code, setCode] = useState('');

  // Adding state to hold question details fetched from the API
  const [questionDetails, setQuestionDetails] = useState({ title: '', description: '' });

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

  return (
    <div className="App">
      <HeaderApp /> 
      <div className="content">
        <div className="left-container">
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
      <CodeEditor language={activeLanguage} code={code} setCode={setCode} />
    </div>
        </div>
      </div>
  );
}

export default App;
