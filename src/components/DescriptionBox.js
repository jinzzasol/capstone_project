// DescriptionBox.js
import React from 'react';
import '../css/DescriptionBox.css';

const DescriptionBox = ({ title, description }) => {
  return (
    <div className="description-box">
      <div className="description-tab">Description</div>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
};

export default DescriptionBox;
