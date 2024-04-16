// CodeEditor.js
import React, { useEffect, useRef, useState } from 'react';
import AceEditor from 'react-ace';
import '../css/CodeEditor.css'

import 'ace-builds/src-noconflict/mode-python'; 
import 'ace-builds/src-noconflict/mode-c_cpp';
import 'ace-builds/src-noconflict/mode-java';
import 'ace-builds/src-noconflict/theme-monokai'; 
import 'ace-builds/src-noconflict/ext-language_tools';

const CodeEditor = ({ language, code, setCode }) => {
  const modes = {
    python: 'python',
    cpp: 'c_cpp',
    java: 'java',
  };

  const aceEditorRef = useRef(null);

  onst [tooltip, setTooltip] = useState({ visible: false, content: '', x: 0, y: 0 });

    useEffect(() => {
        const editor = aceEditorRef.current.editor;
        if (editor) {
            // Handle mouse move event to show tooltips
            editor.container.addEventListener('mousemove', handleMouseMove);
        }

        return () => {
            if (editor) {
                // Clean up event listener
                editor.container.removeEventListener('mousemove', handleMouseMove);
            }
        };
    }, [suggestions]);

    const handleMouseMove = (event) => {
        const editor = aceEditorRef.current.editor;
        const { row } = editor.renderer.screenToTextCoordinates(event.clientX, event.clientY);
        const suggestion = suggestions.find(s => s.line - 1 === row);
        if (suggestion) {
            setTooltip({
                visible: true,
                content: suggestion.description,
                x: event.clientX,
                y: event.clientY
            });
        } else {
            setTooltip({ ...tooltip, visible: false });
        }
    };

    return (
        <>
            <AceEditor
                ref={aceEditorRef}
                mode={modes[language]}
                theme="monokai"
                value={code}
                onChange={setCode}
                name="UNIQUE_ID_OF_DIV"
                editorProps={{ $blockScrolling: true }}
                setOptions={{
                    enableBasicAutocompletion: true,
                    enableLiveAutocompletion: true,
                    enableSnippets: true,
                }}
            />
            {tooltip.visible && (
                <div style={{
                    position: 'absolute',
                    left: tooltip.x + 'px',
                    top: tooltip.y + 'px',
                    backgroundColor: 'white',
                    border: '1px solid black',
                    padding: '5px',
                    zIndex: 100
                }}>
                    {tooltip.content}
                </div>
            )}
        </>
    );
};

export default CodeEditor;