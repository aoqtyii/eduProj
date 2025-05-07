import apiClient from './api'; // Import the configured Axios instance

// Function to call the login endpoint
export const loginUser = async (credentials) => {
  try {
    // Backend expects 'username' and 'password' in form data for OAuth2PasswordRequestForm
    // We need to send it as 'x-www-form-urlencoded'
    const formData = new URLSearchParams();
    formData.append('username', credentials.username); // Assuming frontend sends 'username' which maps to email
    formData.append('password', credentials.password);

    const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    // Assuming backend returns { access_token: '...', token_type: 'bearer' }
    return response.data;
  } catch (error) {
    console.error('Error in loginUser service:', error);
    throw error;
  }
};

// Function to register a new user
export const registerUser = async (userInfo) => {
    // userInfo should match backend's UserRegister schema: {email, password, full_name?}
    try {
        const response = await apiClient.post('/auth/register', userInfo);
        // Backend returns the created user data (schemas.User)
        return response.data;
    } catch (error) {
        console.error('Error in registerUser service:', error);
        throw error;
    }
};

// Function to request a password reset
export const requestPasswordReset = async (identifier) => {
  try {
    // Backend expects {"identifier": "user@example.com"}
    const response = await apiClient.post('/auth/forgot-password', { identifier });
    // Backend returns a message like: {"message": "..."}
    return response.data;
  } catch (error) {
    console.error('Error in requestPasswordReset service:', error);
    throw error; // Re-throw might be okay here, depends on desired UX
  }
};

// Function to reset password using a token
export const resetPassword = async (resetData) => {
    // resetData should match backend's PasswordResetRequest schema: {token, new_password}
    try {
        const response = await apiClient.post('/auth/reset-password', resetData);
        // Backend returns a message like: {"message": "Password has been reset successfully."}
        return response.data;
    } catch (error) {
        console.error('Error in resetPassword service:', error);
        throw error;
    }
};


// Function to call the logout endpoint (optional)
export const logoutUser = async () => {
  try {
    // No backend endpoint for logout defined in the provided code.
    // If added later, uncomment and implement the call:
    // await apiClient.post('/auth/logout');
    return true; // Indicate client-side logout success
  } catch (error) {
    console.error('Error in logoutUser service:', error);
    throw error;
  }
};