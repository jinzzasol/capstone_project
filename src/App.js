// App.js
import React, {useState} from 'react';
import './App.css';
import HeaderApp from './components/HeaderApp'; 
import DescriptionBox from './components/DescriptionBox';
import CodeEditor from './components/CodeEditor';
import CodeTabs from './components/CodeTabs';
import questions from './data/questions';

function App() {

 
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  const [activeLanguage, setActiveLanguage] = useState('python');
  const [code, setCode] = useState('');
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
        title={questions[currentQuestionIndex].title} 
        description={questions[currentQuestionIndex].description}
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
