import apiClient from './api';

// Function to get the current user's profile info
export const getMe = async () => {
    try {
        const response = await apiClient.get('/users/me');
        // Backend returns user data based on schemas.User
        return response.data;
    } catch (error) {
        console.error('Error fetching current user data:', error);
        throw error;
    }
};

// Function to update the current user's profile info
export const updateMe = async (updateData) => {
    // updateData should match backend's UserUpdate schema: {email?, full_name?, password?}
    try {
        const response = await apiClient.put('/users/me', updateData);
        // Backend returns updated user data based on schemas.User
        return response.data;
    } catch (error) {
        console.error('Error updating user profile:', error);
        throw error;
    }
};

// Add other user-related API calls if backend implements them later (e.g., admin functions)