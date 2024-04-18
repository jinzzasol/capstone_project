/* Code Editor.css */
import React, { useEffect, useRef, useState } from 'react';
import AceEditor from 'react-ace';
import '../css/CodeEditor.css'

import '../css/CodeEditor.css';
import 'ace-builds/src-noconflict/mode-python'; 
import 'ace-builds/src-noconflict/mode-c_cpp';
import 'ace-builds/src-noconflict/mode-java';
import 'ace-builds/src-noconflict/theme-monokai'; 

const CodeEditor = ({
  language,
  code,
  setCode,
  onNewLineAdded,
  highlightedLine,
  tooltipText,
  setTooltipVisible,
  tooltipVisible
}) => {
  const editorRef = useRef(null);
  const [tooltipPosition, setTooltipPosition] = useState({ left: 0, top: 0 });

  // Mode configuration based on the language prop
  const modes = {
    python: 'python',
    cpp: 'c_cpp',
    java: 'java',
  };

  const handleCloseTooltip = (event) => {
    event.stopPropagation();  // This stops the click event from bubbling up to other elements
    setTooltipVisible(false);
  };
  // Handle dynamic code changes
  const handleCodeChange = (newCode) => {
    setCode(newCode);
    if (newCode.endsWith('\n')) {
      const lines = newCode.split('\n');
      const currentLine = lines[lines.length - 2]; // The second last line is the last complete line
      onNewLineAdded(currentLine, lines.length - 2);
    }
  };

  // Effect for highlighting lines
  useEffect(() => {
    const editor = editorRef.current && editorRef.current.editor;
    const session = editor && editor.getSession();
    
    if (editor && highlightedLine !== null) {
      // Clear existing markers
      session.clearMarkers();

      // Highlight new line
      session.addMarker(new Range(highlightedLine, 0, highlightedLine, 1), "highlighted-line", "fullLine");
    }
  }, [highlightedLine]);

  // Effect for showing tooltips
  useEffect(() => {
    if (tooltipVisible && editorRef.current) {
      const editor = editorRef.current.editor;
      const handleCursorChange = () => {
        const { row, column } = editor.getCursorPosition();
        const screenPos = editor.renderer.textToScreenCoordinates(row, column);
        setTooltipPosition({ left: screenPos.pageX + 10, top: screenPos.pageY + 10 });
      };

      editor.on('changeCursor', handleCursorChange);
      return () => {
        editor.off('changeCursor', handleCursorChange);
      };
    }
  }, [tooltipVisible]);

  return (
    <>
      <AceEditor
        ref={editorRef}
        className="ace-editor"
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
      {tooltipVisible && (
        <div className="tooltip" style={{ position: 'absolute', left: tooltipPosition.left, top: tooltipPosition.top }}>
          {tooltipText}
          <button className="tooltip-close-button" onClick={handleCloseTooltip}>&times;</button>
        </div>
      )}
    </>
  );
};

export default CodeEditor;
