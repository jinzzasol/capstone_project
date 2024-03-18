// CodeEditor.js
import React from 'react';
import AceEditor from 'react-ace';
import '../css/CodeEditor.css'

import 'ace-builds/src-noconflict/mode-python'; 
import 'ace-builds/src-noconflict/mode-c_cpp';
import 'ace-builds/src-noconflict/mode-java';
import 'ace-builds/src-noconflict/theme-monokai'; 

const CodeEditor = ({ language, code, setCode }) => {
  const modes = {
    python: 'python',
    cpp: 'c_cpp',
    java: 'java',
  };

  return (
    <>
    <AceEditor className="ace-editor"
      mode={modes[language]}
      theme="monokai"
      value={code} //code content 
      onChange={setCode} 
      name="UNIQUE_ID_OF_DIV"
      editorProps={{ $blockScrolling: true }}
      setOptions={{
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        enableSnippets: true
      }}
    />
    </>
  );
};

export default CodeEditor;
