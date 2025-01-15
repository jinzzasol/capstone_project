// lib/codeHandler.js
import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://52.91.5.78:7070',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const sendCodeToBackend = async (code, questionId, submissionId) => {
  try {
    const response = await instance.post('/api/submit-code', {
      code: code,
      questionId: questionId,
      submissionId: submissionId,
    });
    console.log('Response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error sending code to backend:', error);
    throw error;
  }
};
