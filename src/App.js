// App.js
import React, {useState} from 'react';
import './App.css';
import HeaderApp from './components/HeaderApp'; 
import DescriptionBox from './components/DescriptionBox';
import CodeEditor from './components/CodeEditor';
import CodeTabs from './components/CodeTabs';

function App() {
  const [activeLanguage, setActiveLanguage] = useState('python');
  const [code, setCode] = useState('');

  return (
    <div className="App">
      <HeaderApp /> 
      <div className="content">
        <div className="left-container">
          <DescriptionBox 
            title="2. Add Two Numbers" 
            description="You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list. You may assume the two numbers do not contain any leading zero, except the number 0 itself. Example 1: Input: l1 = [2,4,3], l2 = [5,6,4] Output: [7,0,8] Explanation: 342 + 465 = 807. Example 2: Input: l1 = [0], l2 = [0] Output: [0] Example 3: Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9] Output: [8,9,9,9,0,0,0,1]"
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
