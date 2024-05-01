import React from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import jwtDecode from 'jwt-decode';
import { useHistory } from 'react-router-dom';

function LoginPage() {
  const history = useHistory();

  const handleLoginSuccess = (response) => {
    const user = jwtDecode(response.credential);
    console.log('User:', user);
    // You can set the user details in state or context for further use
    history.push('/home'); // Redirect to home on successful login
  };

  return (
    <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
      <div>
        <h2>Login Page</h2>
        <GoogleLogin
          onSuccess={handleLoginSuccess}
          onError={() => console.log('Login Failed')}
        />
      </div>
    </GoogleOAuthProvider>
  );
}

export default LoginPage;
