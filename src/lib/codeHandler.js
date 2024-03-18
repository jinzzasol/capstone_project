// lib/codeHandler.js
import axios from 'axios';

export const sendCodeToBackend = async (code, questionId, submissionId) => {
  try {
    const response = await axios.post('http://localhost:7070/submit-code', {
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
