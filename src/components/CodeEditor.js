/* Code Editor.js */
import React, { useEffect, useRef, useState } from 'react';
import AceEditor from 'react-ace';
import '../css/CodeEditor.css'

import '../css/CodeEditor.css';
import 'ace-builds/src-noconflict/mode-python'; 
import 'ace-builds/src-noconflict/mode-c_cpp';
import 'ace-builds/src-noconflict/mode-java';
import 'ace-builds/src-noconflict/theme-monokai'; 
import ace from 'ace-builds';

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
  const markerIdRef = useRef(null);

  useEffect(() => {
    const editor = editorRef.current && editorRef.current.editor;
    const session = editor && editor.getSession();
    const Range = ace.require('ace/range').Range;
  
    // Initialize a ref to store the current marker ID

  
    if (session && highlightedLine !== null) {
      // Remove the existing marker if it exists
      if (markerIdRef.current !== null) {
        session.removeMarker(markerIdRef.current);
      }
  
      // Highlight the new line and update the marker ID
      markerIdRef.current = session.addMarker(new Range(highlightedLine, 0, highlightedLine, 1), "highlighted-line", "fullLine");
    }
  }, [highlightedLine]);
  // Effect for showing tooltips
  useEffect(() => {
    if (tooltipVisible && editorRef.current) {
      const editor = editorRef.current.editor;
      const session = editor.getSession();
  
      const handleCursorChange = () => {
        if (highlightedLine !== null) {
          const screenPosition = editor.renderer.textToScreenCoordinates(highlightedLine, 0); // Get coordinates for the start of the highlighted line
          // Adjust to set the tooltip right beside the highlighted line using the scroller's position
          setTooltipPosition({
            left: screenPosition.pageX - editor.renderer.scroller.getBoundingClientRect().left + editor.renderer.scrollLeft + 10, // Adjust the '10' if needed to position beside the line
            top: screenPosition.pageY - editor.renderer.scroller.getBoundingClientRect().top + editor.renderer.scrollTop,
          });
        }
      };
  
      // Add event listener for cursor change
      editor.on('changeCursor', handleCursorChange);
      // Trigger once initially in case the cursor doesn't move
      handleCursorChange();
  
      // Clean up event listener
      return () => {
        editor.off('changeCursor', handleCursorChange);
      };
    }
  }, [tooltipVisible, highlightedLine, editorRef]);
  

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
        <div className="tooltip" style={{  position: 'absolute', left: tooltipPosition.left, top: tooltipPosition.top }}>
          {tooltipText}
          <button className="tooltip-close-button" onClick={handleCloseTooltip}>&times;</button>
        </div>
      )}
    </>
  );
};

export default CodeEditor;
