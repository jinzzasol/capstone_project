// DescriptionBox.js
import React from 'react';
import DOMPurify from 'dompurify';
import '../css/DescriptionBox.css';

const DescriptionBox = ({ title, description, onPreviousClick, onNextClick, isFirst, isLast }) => {
  const createMarkup = (htmlContent) => {
    return { __html: DOMPurify.sanitize(htmlContent) };
  };

  return (
    <div className="description-box">
      <div className="description-tab">Description</div>
      <h2>{title}</h2>
      <div dangerouslySetInnerHTML={createMarkup(description)} />
      <div className="description-navigation">
        <button onClick={onPreviousClick} disabled={isFirst}>Previous</button>
        <button onClick={onNextClick} disabled={isLast}>Next</button>
      </div>
    </div>
  );
};

export default DescriptionBox;
