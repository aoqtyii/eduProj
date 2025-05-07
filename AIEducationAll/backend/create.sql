-- Optional: Function to update 'updated_at' timestamp automatically
-- (Same as in your create.sql)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Users Table (Based on models/user.py)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users (email);
-- Primary key index (idx_users_id) is created automatically

-- Trigger for users updated_at
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Password Reset Token Table (Based on models/password_reset_token.py)
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE NOT NULL
);

-- Indexes for password_reset_tokens table
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens (token);
CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens (user_id);


-- Courses Table (Based on models/course.py)
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- Matches model FK
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for courses table
CREATE INDEX idx_courses_title ON courses (title);
-- Index on creator_id might be useful depending on queries
-- CREATE INDEX idx_courses_creator_id ON courses (creator_id);

-- Trigger for courses updated_at
CREATE TRIGGER update_courses_updated_at
BEFORE UPDATE ON courses
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Lessons Table (Based on models/lesson.py)
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    "order" INTEGER DEFAULT 0, -- Use quotes for reserved keyword 'order'
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE, -- Matches model FK
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for lessons table
CREATE INDEX idx_lessons_title ON lessons (title);
CREATE INDEX idx_lessons_course_id ON lessons (course_id);

-- Trigger for lessons updated_at
CREATE TRIGGER update_lessons_updated_at
BEFORE UPDATE ON lessons
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Enrollments Table (Based on models/enrollment.py)
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Matches model FK
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE, -- Matches model FK
    enrollment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_user_course_enrollment UNIQUE (user_id, course_id) -- Matches model UniqueConstraint
);

-- Indexes for enrollments table
CREATE INDEX idx_enrollments_user_id ON enrollments (user_id);
CREATE INDEX idx_enrollments_course_id ON enrollments (course_id);


-- Progress Table (Based on models/progress.py)
CREATE TABLE progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Matches model FK
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE, -- Matches model FK
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    score FLOAT, -- Corresponds to SQLAlchemy Float
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_user_lesson_progress UNIQUE (user_id, lesson_id) -- Matches model UniqueConstraint
);

-- Indexes for progress table
CREATE INDEX idx_progress_user_id ON progress (user_id);
CREATE INDEX idx_progress_lesson_id ON progress (lesson_id);

-- v0.1
-- =============================================
-- Practice Center Tables
-- =============================================

-- Practice Modules Table
-- Groups questions, potentially linked to a course or standalone
CREATE TABLE practice_modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL, -- Optional link to a course
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for practice_modules table
CREATE INDEX idx_practice_modules_title ON practice_modules (title);
CREATE INDEX idx_practice_modules_course_id ON practice_modules (course_id);

-- Trigger for practice_modules updated_at
CREATE TRIGGER update_practice_modules_updated_at
BEFORE UPDATE ON practice_modules
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Practice Questions Table
CREATE TABLE practice_questions (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES practice_modules(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL, -- e.g., 'multiple_choice', 'fill_in_blank', 'coding'
    difficulty SMALLINT DEFAULT 1, -- e.g., 1 (easy) to 5 (hard)
    hints TEXT, -- Optional hints
    explanation TEXT, -- Optional explanation shown after answering
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for practice_questions table
CREATE INDEX idx_practice_questions_module_id ON practice_questions (module_id);
CREATE INDEX idx_practice_questions_type ON practice_questions (question_type);

-- Trigger for practice_questions updated_at
CREATE TRIGGER update_practice_questions_updated_at
BEFORE UPDATE ON practice_questions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Practice Answers Table (for multiple choice questions)
CREATE TABLE practice_answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES practice_questions(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE NOT NULL,
    display_order SMALLINT DEFAULT 0
);

-- Indexes for practice_answers table
CREATE INDEX idx_practice_answers_question_id ON practice_answers (question_id);


-- Practice Sessions Table
-- Represents a single instance of a user taking a practice module
CREATE TABLE practice_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES practice_modules(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE, -- Timestamp when completed
    score FLOAT, -- Overall score for the session
    status VARCHAR(50) DEFAULT 'in_progress' NOT NULL -- e.g., 'in_progress', 'completed'
);

-- Indexes for practice_sessions table
CREATE INDEX idx_practice_sessions_user_id ON practice_sessions (user_id);
CREATE INDEX idx_practice_sessions_module_id ON practice_sessions (module_id);
CREATE INDEX idx_practice_sessions_status ON practice_sessions (status);


-- Practice Attempts Table
-- Records a user's answer to a specific question within a session
CREATE TABLE practice_attempts (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES practice_sessions(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES practice_questions(id) ON DELETE CASCADE,
    user_answer_text TEXT, -- For fill-in-blank, coding, or storing selected answer text
    selected_answer_id INTEGER REFERENCES practice_answers(id) ON DELETE SET NULL, -- FK to practice_answers if multiple choice
    is_correct BOOLEAN, -- Result of the attempt
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    feedback TEXT -- Optional specific feedback for this attempt
    -- CONSTRAINT uq_session_question_attempt UNIQUE (session_id, question_id) -- Allow multiple attempts per question in a session? Or only one final? Decide based on logic.
);

-- Indexes for practice_attempts table
CREATE INDEX idx_practice_attempts_session_id ON practice_attempts (session_id);
CREATE INDEX idx_practice_attempts_question_id ON practice_attempts (question_id);
CREATE INDEX idx_practice_attempts_selected_answer_id ON practice_attempts (selected_answer_id);

-- v0.2
-- =============================================
-- 错题本功能相关表
-- =============================================

-- 错题本条目表
CREATE TABLE mistake_notebook_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,           -- 用户外键，用户删除时级联删除条目
    question_id INTEGER NOT NULL REFERENCES practice_questions(id) ON DELETE CASCADE, -- 练习题目外键，题目删除时级联删除条目
    -- original_attempt_id INTEGER REFERENCES practice_attempts(id) ON DELETE SET NULL, -- 可选：关联到具体的错误尝试记录
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 添加时间
    status VARCHAR(50) DEFAULT 'new' NOT NULL,                           -- 状态 ('new', 'reviewed', 'mastered')
    notes TEXT,                                                             -- 用户笔记 (可选)
    last_reviewed_at TIMESTAMP WITH TIME ZONE,                             -- 上次复习时间 (可选)

    -- 确保一个用户对同一个问题只有一条错题记录
    CONSTRAINT uq_user_question_mistake UNIQUE (user_id, question_id)
);

-- 为常用查询添加索引
CREATE INDEX idx_mistake_notebook_user_id ON mistake_notebook_entries (user_id);
CREATE INDEX idx_mistake_notebook_question_id ON mistake_notebook_entries (question_id);
CREATE INDEX idx_mistake_notebook_user_status ON mistake_notebook_entries (user_id, status);

-- 注意：如果需要自动更新 'updated_at' 字段（如果添加的话），也需要为此表创建触发器。
-- 目前设计中没有 'updated_at'，但可以根据需要添加。

-- v0.3
-- =============================================
-- AI Analysis Enhancement Tables (v0.3)
-- =============================================

-- Knowledge Points Table
-- Stores individual concepts, skills, or topics
CREATE TABLE knowledge_points (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL, -- e.g., "Python Variables", "SQL JOIN Types"
    description TEXT,
    subject_area VARCHAR(100),      -- Optional: e.g., "Python", "SQL", "Web Development"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX idx_knowledge_points_name ON knowledge_points (name);
CREATE INDEX idx_knowledge_points_subject ON knowledge_points (subject_area);

-- Question <-> Knowledge Point Mapping Table
-- Many-to-many relationship between questions and knowledge points
CREATE TABLE question_knowledge_points (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES practice_questions(id) ON DELETE CASCADE,
    knowledge_point_id INTEGER NOT NULL REFERENCES knowledge_points(id) ON DELETE CASCADE,
    -- Optional: relevance score or primary topic flag
    -- relevance FLOAT DEFAULT 1.0,
    CONSTRAINT uq_question_knowledge_point UNIQUE (question_id, knowledge_point_id)
);
CREATE INDEX idx_qkp_question_id ON question_knowledge_points (question_id);
CREATE INDEX idx_qkp_knowledge_point_id ON question_knowledge_points (knowledge_point_id);


-- Recommendations Table
-- Stores generated recommendations for users
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL, -- 'practice_module', 'knowledge_point', 'specific_question_type'
    related_item_id INTEGER,                 -- ID of the module, knowledge_point etc.
    related_item_name VARCHAR(255),          -- Denormalized name for easy display
    reason TEXT,                             -- Why this was recommended (e.g., "High error rate in related questions")
    priority SMALLINT DEFAULT 0,             -- Recommendation priority (0=low, 1=medium, 2=high)
    status VARCHAR(50) DEFAULT 'active' NOT NULL, -- 'active', 'dismissed', 'completed' (by user action)
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE      -- Optional: If recommendations should expire
);
CREATE INDEX idx_recommendations_user_id ON recommendations (user_id);
CREATE INDEX idx_recommendations_user_status ON recommendations (user_id, status);
CREATE INDEX idx_recommendations_type ON recommendations (recommendation_type);