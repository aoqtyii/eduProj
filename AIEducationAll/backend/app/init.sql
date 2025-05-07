-- =============================================
-- WARNING: REPLACE PASSWORD PLACEHOLDERS BELOW
-- Use your backend's get_password_hash function
-- =============================================

-- Insert Users
-- User 1: Admin/Course Creator
INSERT INTO users (email, full_name, hashed_password, is_active, is_superuser) VALUES
('admin@example.com', 'Admin User', 'hashed_password_placeholder_for_admin', TRUE, TRUE);

-- User 2: Regular Student
INSERT INTO users (email, full_name, hashed_password, is_active, is_superuser) VALUES
('student@example.com', 'Student User', 'hashed_password_placeholder_for_student', TRUE, FALSE);

-- =============================================
-- The following inserts assume the user IDs are 1 (admin) and 2 (student)
-- Adjust if necessary based on your actual user IDs.
-- =============================================

-- Insert Courses (Created by Admin User, ID=1 assumed)
INSERT INTO courses (title, description, creator_id) VALUES
('Introduction to Python', 'Learn the basics of Python programming.', 1),
('Web Development Basics', 'Introduction to HTML, CSS, and JavaScript.', 1);

-- =============================================
-- The following inserts assume the course IDs are 1 (Python) and 2 (Web Dev)
-- Adjust if necessary based on your actual course IDs.
-- =============================================

-- Insert Lessons for Course 1 (Python, ID=1 assumed)
INSERT INTO lessons (title, content, "order", course_id) VALUES
('Variables and Data Types', 'Understanding variables, integers, floats, strings, etc.', 1, 1),
('Control Flow (If/Else)', 'Using conditional statements.', 2, 1),
('Loops (For/While)', 'Repeating actions with loops.', 3, 1);

-- Insert Lessons for Course 2 (Web Dev, ID=2 assumed)
INSERT INTO lessons (title, content, "order", course_id) VALUES
('HTML Fundamentals', 'Structure of a web page.', 1, 2),
('CSS Basics', 'Styling HTML elements.', 2, 2),
('Introduction to JavaScript', 'Adding interactivity.', 3, 2);


-- =============================================
-- The following inserts assume User ID=2 (student), Course IDs=1,2, and Lesson IDs=1,2,3 for Course 1 and 4,5,6 for Course 2
-- Adjust if necessary based on your actual IDs.
-- =============================================

-- Insert Enrollments (Student User ID=2 assumed)
INSERT INTO enrollments (user_id, course_id) VALUES
(2, 1), -- Student enrolls in Python course
(2, 2); -- Student enrolls in Web Dev course

-- Insert Sample Progress (Student User ID=2 assumed)
-- Assuming Lesson 'Variables and Data Types' has ID=1 and 'HTML Fundamentals' has ID=4
-- Student completed the first Python lesson
INSERT INTO progress (user_id, lesson_id, completed, score, completed_at, last_accessed_at) VALUES
(2, 1, TRUE, 95.0, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day');

-- Student accessed the first Web Dev lesson but hasn't completed it
INSERT INTO progress (user_id, lesson_id, completed, score, last_accessed_at) VALUES
(2, 4, FALSE, NULL, NOW());


-- v0.2
-- =============================================
-- 模拟数据: 练习中心
-- 假设:
--   - 用户 'student@example.com' 的 ID 是 2
--   - 课程 'Introduction to Python' 的 ID 是 1
-- 请根据您的实际 ID 进行调整
-- =============================================

-- 1. 插入练习模块 (Practice Modules)
-- 模块 1: Python 基础语法练习 (关联到 Python 课程)
INSERT INTO practice_modules (title, description, course_id, created_at, updated_at) VALUES
('Python 基础语法测验', '测试你对 Python 变量、数据类型和基本控制流的理解。', 1, NOW(), NOW()) -- 关联到 course_id=1
RETURNING id; -- 获取新插入模块的 ID，假设返回 ID 为 1

-- 模块 2: SQL 基础练习 (独立模块)
INSERT INTO practice_modules (title, description, course_id, created_at, updated_at) VALUES
('SQL 基础查询练习', '练习 SELECT, WHERE, ORDER BY 等基本 SQL 查询语句。', NULL, NOW(), NOW()) -- 不关联课程
RETURNING id; -- 假设返回 ID 为 2

-- 2. 插入练习题目 (Practice Questions) 和 答案 (Practice Answers) for Module 1 (ID=1)

-- 问题 1 (单选题)
INSERT INTO practice_questions (module_id, question_text, question_type, difficulty, explanation, created_at, updated_at) VALUES
(1, '在 Python 中，用于存储整数的数据类型是？', 'multiple_choice', 1, '`int` 代表整数，`float` 代表浮点数（小数），`str` 代表字符串，`bool` 代表布尔值。', NOW(), NOW())
RETURNING id; -- 假设返回 ID 为 1
-- 问题 1 的答案
INSERT INTO practice_answers (question_id, answer_text, is_correct, display_order) VALUES
(1, 'int', TRUE, 1),
(1, 'float', FALSE, 2),
(1, 'str', FALSE, 3),
(1, 'bool', FALSE, 4);

-- 问题 2 (单选题)
INSERT INTO practice_questions (module_id, question_text, question_type, difficulty, explanation, created_at, updated_at) VALUES
(1, '哪个关键字用于在 Python 中定义一个函数？', 'multiple_choice', 1, '使用 `def` 关键字来定义函数。', NOW(), NOW())
RETURNING id; -- 假设返回 ID 为 2
-- 问题 2 的答案
INSERT INTO practice_answers (question_id, answer_text, is_correct, display_order) VALUES
(2, 'func', FALSE, 1),
(2, 'define', FALSE, 2),
(2, 'def', TRUE, 3),
(2, 'function', FALSE, 4);

-- 问题 3 (填空题) - 注意：填空题的正确答案也需插入 answers 表用于后台比对
INSERT INTO practice_questions (module_id, question_text, question_type, difficulty, explanation, created_at, updated_at) VALUES
(1, 'Python 中表示 "不等于" 的运算符是 _____ 。', 'fill_in_blank', 2, '`!=` 用于比较两个值是否不相等。', NOW(), NOW())
RETURNING id; -- 假设返回 ID 为 3
-- 问题 3 的答案 (后台评分用)
INSERT INTO practice_answers (question_id, answer_text, is_correct) VALUES
(3, '!=', TRUE);


-- 3. 插入练习题目 (Practice Questions) 和 答案 (Practice Answers) for Module 2 (ID=2)

-- 问题 4 (单选题)
INSERT INTO practice_questions (module_id, question_text, question_type, difficulty, explanation, created_at, updated_at) VALUES
(2, '哪个 SQL 关键字用于从数据库表中检索数据？', 'multiple_choice', 1, '`SELECT` 语句用于查询数据。', NOW(), NOW())
RETURNING id; -- 假设返回 ID 为 4
-- 问题 4 的答案
INSERT INTO practice_answers (question_id, answer_text, is_correct, display_order) VALUES
(4, 'GET', FALSE, 1),
(4, 'SELECT', TRUE, 2),
(4, 'FETCH', FALSE, 3),
(4, 'RETRIEVE', FALSE, 4);

-- 问题 5 (单选题)
INSERT INTO practice_questions (module_id, question_text, question_type, difficulty, explanation, created_at, updated_at) VALUES
(2, '哪个 SQL 子句用于过滤查询结果？', 'multiple_choice', 1, '`WHERE` 子句用于根据指定条件过滤记录。', NOW(), NOW())
RETURNING id; -- 假设返回 ID 为 5
-- 问题 5 的答案
INSERT INTO practice_answers (question_id, answer_text, is_correct, display_order) VALUES
(5, 'FILTER BY', FALSE, 1),
(5, 'HAVING', FALSE, 2), -- HAVING 通常用于 GROUP BY 之后
(5, 'WHERE', TRUE, 3),
(5, 'LIMIT', FALSE, 4); -- LIMIT 用于限制返回行数

-- 4. 插入练习会话 (Practice Sessions) for User ID=2

-- 为用户 2 开始一个关于模块 1 (Python 基础) 的会话，并标记为已完成
INSERT INTO practice_sessions (user_id, module_id, started_at, completed_at, score, status) VALUES
(2, 1, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes', 50.0, 'completed') -- 假设得了 50 分
RETURNING id; -- 假设返回 ID 为 1 (这是 session_id)


-- 5. 插入练习尝试 (Practice Attempts) for Session ID=1 (User 2 on Module 1)
-- 假设问题 1 的答案 ID 分别是 1(T), 2(F), 3(F), 4(F)
-- 假设问题 2 的答案 ID 分别是 5(F), 6(F), 7(T), 8(F)
-- 假设问题 3 的答案 ID 是 9(T)

-- 尝试 问题 1 (选择错误答案 ID=2)
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at, feedback) VALUES
(1, 1, 2, NULL, FALSE, NOW() - INTERVAL '45 minutes', NULL);

-- 尝试 问题 2 (选择正确答案 ID=7)
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at, feedback) VALUES
(1, 2, 7, NULL, TRUE, NOW() - INTERVAL '40 minutes', NULL);

-- 尝试 问题 3 (填空题，回答错误)
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at, feedback) VALUES
(1, 3, NULL, '<>', FALSE, NOW() - INTERVAL '35 minutes', '注意比较运算符的写法。'); -- 假设自动评分逻辑判定为错误

-- 注意: 上述尝试数据模拟了用户在会话中逐步提交答案的过程。
-- 在实际应用中，`submitSessionAnswers` API 会一次性创建所有尝试记录，并计算 is_correct 和 score。
-- 上面的 `practice_sessions` score=50.0 是基于问题 2 回答正确，问题 1 和 3 回答错误 (1/3 * 100 = 33.3，这里写 50 只是示例)。
-- 你可能需要调整 score 或 attempts 的 is_correct 来匹配。

-- v0.3
-- =============================================
-- 模拟数据 v0.3: AI 分析相关增强
-- 假设:
--   - student@example.com 用户 ID 为 2
--   - 'Python 基础语法测验' 模块 ID 为 1
--   - 'SQL 基础查询练习' 模块 ID 为 2
--   - Python 基础模块的问题 ID 为 1, 2, 3
--   - SQL 基础模块的问题 ID 为 4, 5
-- 请根据实际情况调整 ID
-- =============================================

-- 1. 插入更多练习会话和尝试 (用于统计练习表现)

-- 会话 2: 用户 2 再次尝试 Python 基础 (Module 1), 得分较高
INSERT INTO practice_sessions (user_id, module_id, started_at, completed_at, score, status) VALUES
(2, 1, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '15 minutes', 100.0, 'completed')
RETURNING id; -- 假设返回 session_id = 2

-- 尝试记录 for Session 2 (全部正确)
-- 问题 1 (ID=1), 正确答案 ID=1
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at) VALUES
(2, 1, 1, NULL, TRUE, NOW() - INTERVAL '2 days' + INTERVAL '5 minutes');
-- 问题 2 (ID=2), 正确答案 ID=7
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at) VALUES
(2, 2, 7, NULL, TRUE, NOW() - INTERVAL '2 days' + INTERVAL '10 minutes');
-- 问题 3 (ID=3), 正确答案文本 '!=' (答案 ID=9)
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at) VALUES
(2, 3, NULL, '!=', TRUE, NOW() - INTERVAL '2 days' + INTERVAL '14 minutes');


-- 会话 3: 用户 2 尝试 SQL 基础 (Module 2), 有对有错
INSERT INTO practice_sessions (user_id, module_id, started_at, completed_at, score, status) VALUES
(2, 2, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '10 minutes', 50.0, 'completed')
RETURNING id; -- 假设返回 session_id = 3

-- 尝试记录 for Session 3
-- 问题 4 (ID=4), 正确答案 ID = (SELECT id FROM practice_answers WHERE question_id=4 AND is_correct=TRUE LIMIT 1)
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at) VALUES
(3, 4, (SELECT id FROM practice_answers WHERE question_id=4 AND is_correct=TRUE LIMIT 1), NULL, TRUE, NOW() - INTERVAL '1 day' + INTERVAL '4 minutes');
-- 问题 5 (ID=5), 错误答案 ID = (SELECT id FROM practice_answers WHERE question_id=5 AND is_correct=FALSE LIMIT 1)
INSERT INTO practice_attempts (session_id, question_id, selected_answer_id, user_answer_text, is_correct, submitted_at) VALUES
(3, 5, (SELECT id FROM practice_answers WHERE question_id=5 AND is_correct=FALSE LIMIT 1), NULL, FALSE, NOW() - INTERVAL '1 day' + INTERVAL '8 minutes');


-- 2. 插入错题本条目 (基于上面的错误尝试)
-- 在 submit_attempts 的 CRUD 操作中已包含自动添加逻辑，但这里可以手动添加以确保数据存在

-- 问题 1 (ID=1) 来自 会话 1 (session_id=1) 的错误尝试
-- 如果 crud_practice.py 中的 submit_attempts 已正确执行，这行可能不需要或会因唯一约束失败
INSERT INTO mistake_notebook_entries (user_id, question_id, added_at, status, notes) VALUES
(2, 1, NOW() - INTERVAL '45 minutes', 'new', '第一次做错了，容易混淆数据类型。')
ON CONFLICT (user_id, question_id) DO NOTHING; -- 如果已存在则忽略

-- 问题 3 (ID=3) 来自 会话 1 (session_id=1) 的错误尝试 (填空题)
INSERT INTO mistake_notebook_entries (user_id, question_id, added_at, status, notes) VALUES
(2, 3, NOW() - INTERVAL '35 minutes', 'new', '运算符 != 没记住。')
ON CONFLICT (user_id, question_id) DO NOTHING;

-- 问题 5 (ID=5) 来自 会话 3 (session_id=3) 的错误尝试
INSERT INTO mistake_notebook_entries (user_id, question_id, added_at, status, notes) VALUES
(2, 5, NOW() - INTERVAL '1 day' + INTERVAL '8 minutes', 'reviewed', '复习过一次，WHERE 和 HAVING 的区别。')
ON CONFLICT (user_id, question_id) DO UPDATE SET status='reviewed', notes='复习过一次，WHERE 和 HAVING 的区别。'; -- 如果存在则更新状态和笔记

-- 添加一个已掌握的错题
INSERT INTO mistake_notebook_entries (user_id, question_id, added_at, status, notes, last_reviewed_at) VALUES
(2, 4, NOW() - INTERVAL '3 days', 'mastered', '这个 SQL 知识点已掌握。', NOW() - INTERVAL '1 day')
ON CONFLICT (user_id, question_id) DO UPDATE SET status='mastered', notes='这个 SQL 知识点已掌握。', last_reviewed_at = NOW() - INTERVAL '1 day';

-- 3. 插入知识点 (Knowledge Points)
INSERT INTO knowledge_points (name, description, subject_area) VALUES
('Python Variables', 'Basic variable assignment and types in Python', 'Python'),
('Python Data Types', 'Integers, Floats, Strings, Booleans in Python', 'Python'),
('Python Control Flow', 'If/Else statements in Python', 'Python'),
('Python Functions', 'Defining and calling functions using def', 'Python'),
('Python Operators', 'Comparison operators like !=', 'Python'),
('SQL SELECT', 'Retrieving data using SELECT statement', 'SQL'),
('SQL WHERE', 'Filtering data using WHERE clause', 'SQL'),
('SQL ORDER BY', 'Sorting query results', 'SQL')
ON CONFLICT (name) DO NOTHING; -- 避免重复插入

-- 4. 关联问题与知识点 (Question <-> Knowledge Point Mapping)
-- 假设知识点 ID 按插入顺序为 1 到 8

-- 问题 1 (Python 整数类型) -> 关联 Python Variables (ID=1), Python Data Types (ID=2)
INSERT INTO question_knowledge_points (question_id, knowledge_point_id) VALUES (1, 1), (1, 2) ON CONFLICT DO NOTHING;
-- 问题 2 (Python 函数定义) -> 关联 Python Functions (ID=4)
INSERT INTO question_knowledge_points (question_id, knowledge_point_id) VALUES (2, 4) ON CONFLICT DO NOTHING;
-- 问题 3 (Python 不等于) -> 关联 Python Operators (ID=5)
INSERT INTO question_knowledge_points (question_id, knowledge_point_id) VALUES (3, 5) ON CONFLICT DO NOTHING;
-- 问题 4 (SQL SELECT) -> 关联 SQL SELECT (ID=6)
INSERT INTO question_knowledge_points (question_id, knowledge_point_id) VALUES (4, 6) ON CONFLICT DO NOTHING;
-- 问题 5 (SQL WHERE) -> 关联 SQL WHERE (ID=7)
INSERT INTO question_knowledge_points (question_id, knowledge_point_id) VALUES (5, 7) ON CONFLICT DO NOTHING;

-- 5. 插入模拟推荐 (Recommendations)
-- 通常由后台服务生成，这里手动插入用于展示
INSERT INTO recommendations (user_id, recommendation_type, related_item_id, related_item_name, reason, priority, status) VALUES
(2, 'practice_module', 1, '练习模块: Python 基础语法测验', '检测到您在 Python 基础知识点上存在一些疑问，建议再次练习巩固。', 1, 'active'),
(2, 'knowledge_point', 5, '知识点: Python Operators', '您似乎对 Python 比较运算符不太熟悉，建议重点复习相关内容。', 1, 'active'),
(2, 'general_review', NULL, NULL, '建议您定期回顾错题本中的题目。', 0, 'dismissed'); -- 假设这条已被忽略