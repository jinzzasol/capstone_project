/*HeaderApp.js*/
import React from 'react';
import '../css/HeaderApp.css'; 
import logo from '../assets/logo192.png';
const HeaderApp = () => {
  return (
    <header className="header-app">
       <img src={logo} alt="Logo" className="logo" />
      <h1>InterviewMentorAI</h1>
    </header>
  );
};

export default HeaderApp;
