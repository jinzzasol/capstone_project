/*CodeTabs.js*/
import React from "react";
import '../css/CodeTabs.css'

const CodeTabs = ({activeLanguage, setActiveLanguage }) => {
    return (
        <>
        <div className="description-tab">
        <span className="symbol">&lt;/&gt;</span> 
        <span className="code-text"> Code</span> 
        </div>
        <div className="code-tabs">
            <button onClick={() => setActiveLanguage('python')} className = {activeLanguage === 'python' ? 'active' : '' }>
                Python
            </button>
            <button onClick={() => setActiveLanguage('cpp')} className = {activeLanguage === 'cpp' ? 'active' : '' }>
                C++
            </button>
            <button onClick={() => setActiveLanguage('java')} className = {activeLanguage === 'java' ? 'active' : '' }>
                Java
            </button>
  
        </div>
        </>
       
    );
};

export default CodeTabs;