aieducation_backend/
├── app/
│   ├── api/                  # API 路由 ( Routers / Controllers )
│   │   ├── __init__.py
│   │   ├── endpoints/        # 各模块的 API 端点
│   │   │   ├── __init__.py
│   │   │   ├── auth.py       # 认证相关接口
│   │   │   ├── courses.py    # 课程
│   │   │   ├── dashboard.py  # Dashboard 相关接口
│   │   │   └── users.py      # 
│   │   └── deps.py           # API 依赖项 (如获取当前用户)
│   ├── core/                 # 核心配置、安全等
│   │   ├── __init__.py
│   │   ├── config.py         # 应用配置 (环境变量、密钥等)
│   │   └── security.py       # 安全相关 (密码哈希, JWT)
│   ├── crud/                 # 数据访问层 (Create, Read, Update, Delete)
│   │   ├── __init__.py
│   │   ├── base.py           # CRUD 基类 (可选)
│   │   ├── crud_course.py
│   │   ├── crud_password_reset_token.py
│   │   ├── crud_user.py
│   │   └── ...               # 其他数据模型的 CRUD 操作
│   ├── db/                   # 数据库
│   │   ├── __init__.py
│   │   ├── base_class.py
│   │   └── session.py
│   ├── models/               # 数据库模型 (如 SQLAlchemy models)
│   │   ├── __init__.py
│   │   ├── course.py
│   │   ├── password_reset_token.py
│   │   └── user.py
│   ├── schemas/              # Pydantic 数据模型 (用于数据校验和序列化)
│   │   ├── __init__.py
│   │   ├── course.py          # Token 相关 schema
│   │   ├── password.py           # User 相关 schema
│   │   ├── token.py          # Token 相关 schema
│   │   ├── user.py           # User 相关 schema
│   │   └── ...
│   ├── services/             # 业务逻辑层 (可选, 可将复杂逻辑放这里)
│   │   ├── __init__.py
│   │   └── ...
│   └── main.py               # FastAPI 应用实例和全局中间件
├── tests/                    # 单元测试和集成测试
│   └── ...
├── .env                      # 环境变量文件
├── requirements.txt          # Python 依赖
└── README.md