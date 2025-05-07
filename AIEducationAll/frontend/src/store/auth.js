import { defineStore } from 'pinia';
// Import your API call functions
import { loginUser, registerUser, requestPasswordReset, resetPassword } from '@/services/auth';
import { getMe } from '@/services/user'; // Import getMe to fetch user data
import router from '@/router'; // Import router for navigation

export const useAuthStore = defineStore('auth', {
  // State
  state: () => ({
    token: localStorage.getItem('authToken') || null,
    user: JSON.parse(localStorage.getItem('authUser') || '{}') || null,
    status: null, // e.g., 'loading', 'success', 'error', 'fetching-user'
  }),

  // Getters
  getters: {
    isAuthenticated: (state) => !!state.token,
    getUser: (state) => state.user,
    getToken: (state) => state.token,
    authStatus: (state) => state.status,
  },

  // Actions
  actions: {
    async login(credentials) {
      this.status = 'loading';
      try {
        // Call the login API service function
        // Expects { access_token, token_type } from backend
        const loginResponse = await loginUser(credentials);

        // Store the token immediately
        this.token = loginResponse.access_token;
        localStorage.setItem('authToken', this.token); // Persist token

        // After successful login and token storage, fetch user details
        this.status = 'fetching-user';
        await this.fetchUserData(); // Call action to get user data

        // Check if user data was fetched successfully
        if (this.user) {
          this.status = 'success';
          // Redirect to dashboard or intended page
          const redirectPath = router.currentRoute.value.query.redirect || '/app/dashboard';
          router.push(redirectPath);
          return true; // Indicate overall success
        } else {
          // Handle case where token was received but user data fetch failed
          throw new Error("Login successful, but failed to fetch user data.");
        }

      } catch (error) {
        // Handle login or user fetch errors
        this.status = 'error';
        this.token = null;
        this.user = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        console.error('Login process failed:', error.response?.data || error.message || error);
        return false; // Indicate failure
      }
    },

    async fetchUserData() {
        // Fetches user data using the stored token
        if (!this.token) {
          console.error("No token available to fetch user data.");
          return; // Exit if no token
        }
        try {
          const userData = await getMe(); // Call the getMe service
          this.user = userData; // Update user state
          localStorage.setItem('authUser', JSON.stringify(this.user)); // Persist user info
        } catch (error) {
          console.error('Failed to fetch user data:', error.response?.data || error.message);
          // Critical error: Token might be valid but user fetch failed. Logout?
          this.logout(); // Force logout if user data can't be fetched with a token
        }
      },

    logout() {
      this.status = 'logging-out';
      this.token = null;
      this.user = null;
      this.status = null;
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
      router.push({ name: 'Login' });
    },

    initializeAuth() {
      const token = localStorage.getItem('authToken');
      const userJson = localStorage.getItem('authUser');
      if (token) {
        this.token = token;
        if (userJson) {
            try {
                this.user = JSON.parse(userJson);
            } catch (e) {
                console.error("Failed to parse user from localStorage", e);
                this.user = null;
                localStorage.removeItem('authUser'); // Clear invalid data
                 // Try fetching user data again if token exists but user data is invalid/missing
                this.fetchUserData();
            }
        } else {
             // If token exists but no user data, fetch it
             this.fetchUserData();
        }
      }
    },

    // Placeholder actions for other auth functionalities
    async register(userInfo) {
        this.status = 'loading';
        try {
            const registeredUser = await registerUser(userInfo);
            this.status = 'registration_success';
            // Optionally log the user in immediately after registration
            // await this.login({ username: userInfo.email, password: userInfo.password });
            return registeredUser; // Return user data (without password)
        } catch (error) {
            this.status = 'error';
            console.error('Registration failed:', error.response?.data || error.message);
            throw error; // Re-throw for component handling
        }
    },

    async forgotPassword(identifier) {
        this.status = 'loading';
        try {
            const response = await requestPasswordReset(identifier);
            this.status = 'forgot_password_requested';
            return response; // Return success message from backend
        } catch (error) {
            this.status = 'error';
            console.error('Forgot password request failed:', error.response?.data || error.message);
            // Avoid throwing specific errors to prevent enumeration attacks
            // Just indicate failure generically in the component
            return false; // Indicate failure
        }
    },

    async confirmResetPassword(resetData) {
        this.status = 'loading';
        try {
            const response = await resetPassword(resetData); // Use the new service function
            this.status = 'reset_password_success';
            return response; // Return success message
        } catch (error) {
            this.status = 'error';
            console.error('Password reset confirmation failed:', error.response?.data || error.message);
            throw error; // Re-throw for component handling
        }
    }
  },
});