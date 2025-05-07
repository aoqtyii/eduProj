XXX-School-Platform/
├── public/                   # Static assets directly copied to build root
│   ├── favicon.ico
│   └── ...
├── src/                      # Main source code
│   ├── assets/               # Assets processed by Vite (CSS, fonts, images)
│   │   ├── fonts/
│   │   ├── images/
│   │   └── styles/
│   │       └── global.css    # Global styles
│   ├── components/           # Reusable UI components (e.g., Button, Modal)
│   │   ├── common/           # General purpose components
│   │   └── layout/           # Layout specific components (Header, Sidebar)
│   ├── core/                 # Core logic, not UI (e.g., offline manager)
│   │   ├── offline/
│   │   └── sync/
│   ├── layouts/              # Page layouts (wrappers for views)
│   │   ├── AuthLayout.vue    # Layout for login, register pages
│   │   └── DefaultLayout.vue # Main layout after login (with nav, header)
│   ├── router/               # Vue Router configuration
│   │   └── index.js
│   ├── services/             # API service definitions (Axios wrappers)
│   │   ├── api.js            # Axios instance configuration
│   │   ├── auth.js           # Auth related API calls
│   │   ├── course.js         # Course/content API calls
│   │   └── ...               # Other modules (learn, practice, etc.)
│   ├── store/                # State management (Pinia)
│   │   ├── index.js          # Pinia setup
│   │   ├── auth.js           # Auth state (token, user info)
│   │   ├── offline.js        # Offline state and management
│   │   └── ...               # Other state modules
│   ├── utils/                # Utility functions (helpers, constants)
│   ├── views/                # Page-level components (mapped to routes)
│   │   ├── auth/
│   │   │   ├── LoginPage.vue
│   │   │   └── ForgotPasswordPage.vue
│   │   ├── dashboard/
│   │   │   └── DashboardPage.vue
│   │   └── ...               # Other sections (Courses, Practice, Profile)
│   ├── App.vue               # Root Vue component
│   └── main.js               # Application entry point
├── .env                      # General environment variables
├── .env.development          # Development specific env variables
├── .env.production           # Production specific env variables
├── .gitignore                # Git ignore file
├── index.html                # Main HTML entry file for Vite
├── package.json              # Project dependencies and scripts
├── README.md                 # Project description
└── vite.config.js            # Vite build tool configuration