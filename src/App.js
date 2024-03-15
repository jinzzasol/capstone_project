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
  description={`<p>You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list. You may assume the two numbers do not contain any leading zero, except the number 0 itself.</p><p><strong>Example 1:</strong><br />Input: l1 = [2,4,3], l2 = [5,6,4]<br />Output: [7,0,8]<br />Explanation: 342 + 465 = 807.</p><p><strong>Example 2:</strong><br />Input: l1 = [0], l2 = [0]<br />Output: [0]</p><p><strong>Example 3:</strong><br />Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]<br />Output: [8,9,9,9,0,0,0,1]</p>`}
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
