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
  tooltipVisible,
  setTooltipVisible,
  handleNextSuggestion,
  handlePreviousSuggestion,
  currentSuggestionIndex,
  suggestions
}) =>  {
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
  const markerIdRef = useRef([]);

  useEffect(() => {
    const editor = editorRef.current && editorRef.current.editor;
    const session = editor && editor.getSession();
    const Range = ace.require('ace/range').Range;
  
    // Clear existing markers
    if (markerIdRef.current.length) {
      markerIdRef.current.forEach(marker => session.removeMarker(marker));
    }
    markerIdRef.current = [];
  
    // Check if highlighted lines are provided and are in an array
    if (session && Array.isArray(highlightedLine) && highlightedLine.length > 0) {
      // Add new markers for each line
      highlightedLine.forEach(line => {
        const markerId = session.addMarker(new Range(line - 1, 0, line - 1, 1), "highlighted-line", "fullLine");
        markerIdRef.current.push(markerId);
      });
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
  <div className="tooltip" style={{ position: 'absolute', left: tooltipPosition.left, top: tooltipPosition.top }}>
    {tooltipText}
    <button className="tooltip-close-button" onClick={handleCloseTooltip}>&times;</button>
    <br></br>
    <button className='button-nav' onClick={handlePreviousSuggestion} disabled={currentSuggestionIndex === 0}>&lt; </button>
    <button className='button-nav' onClick={handleNextSuggestion} disabled={currentSuggestionIndex === suggestions.length - 1}> &gt;</button>
  </div>
)}

    </>
  );
};

export default CodeEditor;
