// App.js
import React, {useState} from 'react';
import './App.css';
import HeaderApp from './components/HeaderApp'; 
import DescriptionBox from './components/DescriptionBox';
import CodeEditor from './components/CodeEditor';
import CodeTabs from './components/CodeTabs';

function App() {

  const questions = [
    {
      id: 1,
      title: "1. Add Two Numbers",
      description: "<p>You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list. You may assume the two numbers do not contain any leading zero, except the number 0 itself.</p><p><strong>Example 1:</strong><br />Input: l1 = [2,4,3], l2 = [5,6,4]<br />Output: [7,0,8]<br />Explanation: 342 + 465 = 807.</p><p><strong>Example 2:</strong><br />Input: l1 = [0], l2 = [0]<br />Output: [0]</p><p><strong>Example 3:</strong><br />Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]<br />Output: [8,9,9,9,0,0,0,1]</p>"
    },
    {
      id: 2,
      title: "2. Two Sum",
      description: "<p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return indices of the two numbers such that they add up to <code>target</code>.</p><p>You may assume that each input would have <strong>exactly one solution</strong>, and you may not use the same element twice.</p><p>You can return the answer in any order.</p><p><strong>Example 1:</strong><br />Input: nums = [2,7,11,15], target = 9<br />Output: [0,1]<br />Output: Because nums[0] + nums[1] == 9, we return [0, 1].</p>"
    },
    {
      id: 3,
      title: "3. Longest Substring Without Repeating Characters",
      description: "<p>Given a string <code>s</code>, find the length of the <strong>longest substring</strong> without repeating characters.</p><p><strong>Example 1:</strong><br />Input: s = \"abcabcbb\"<br />Output: 3<br />Explanation: The answer is \"abc\", with the length of 3.</p><p><strong>Example 2:</strong><br />Input: s = \"bbbbb\"<br />Output: 1<br />Explanation: The answer is \"b\", with the length of 1.</p>"
    },
    {
      id: 4,
      title: "4. Median of Two Sorted Arrays",
      description: "<p>Given two sorted arrays <code>nums1</code> and <code>nums2</code> of size <code>m</code> and <code>n</code> respectively, return the <strong>median</strong> of the two sorted arrays.</p><p>The overall run time complexity should be <code>O(log (m+n))</code>.</p><p><strong>Example 1:</strong><br />Input: nums1 = [1,3], nums2 = [2]<br />Output: 2.00000<br />Explanation: merged array = [1,2,3] and median is 2.</p><p><strong>Example 2:</strong><br />Input: nums1 = [1,2], nums2 = [3,4]<br />Output: 2.50000<br />Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.</p>"
    },
    {
      id: 5,
      title: "5. Longest Palindromic Substring",
      description: "<p>Given a string <code>s</code>, return the <strong>longest palindromic substring</strong> in <code>s</code>.</p><p><strong>Example 1:</strong><br />Input: s = \"babad\"<br />Output: \"bab\"<br />Note: \"aba\" is also a valid answer.</p><p><strong>Example 2:</strong><br />Input: s = \"cbbd\"<br />Output: \"bb\"</p>"
    },
  ];
  
  
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
