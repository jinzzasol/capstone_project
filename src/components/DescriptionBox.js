// DescriptionBox.js
import React from 'react';
import DOMPurify from 'dompurify';
import '../css/DescriptionBox.css';

const DescriptionBox = ({ title, description }) => {
  const createMarkup = (htmlContent) => {
    return { __html: DOMPurify.sanitize(htmlContent) };
  };

  return (
    <div className="description-box">
      <div className="description-tab">Description</div>
      <h2>{title}</h2>
      <div dangerouslySetInnerHTML={createMarkup(description)} />
    </div>
  );
};

export default DescriptionBox;
