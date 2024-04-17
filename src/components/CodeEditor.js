import React from 'react';
import AceEditor from 'react-ace';

import '../css/CodeEditor.css';
import 'ace-builds/src-noconflict/mode-python'; 
import 'ace-builds/src-noconflict/mode-c_cpp';
import 'ace-builds/src-noconflict/mode-java';
import 'ace-builds/src-noconflict/theme-monokai'; 

const CodeEditor = ({ language, code, setCode, onNewLineAdded }) => {
  const modes = {
    python: 'python',
    cpp: 'c_cpp',
    java: 'java',
  };

  const handleCodeChange = (newCode) => {
    setCode(newCode);
    if (newCode.endsWith('\n')) {
      const lines = newCode.split('\n');
      const currentLine = lines[lines.length - 2]; // The second last line is the last complete line
      onNewLineAdded(currentLine);
    }
  };

  return (
    <>
    <AceEditor className="ace-editor"
      mode={modes[language]}
      theme="monokai"
      value={code}
      onChange={handleCodeChange} 
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
