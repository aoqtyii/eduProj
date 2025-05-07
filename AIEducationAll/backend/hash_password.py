# hash_password.py
import sys
import os

# 确保可以导入 app 包 (假设脚本放在 backend 目录下)
# 如果脚本放在其他地方，需要调整路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 从您项目的安全模块导入哈希函数
    from app.core.security import get_password_hash
except ImportError:
    print("错误：无法从 app.core.security 导入 get_password_hash。")
    print("请确保：")
    print("1. 您已经激活了项目的虚拟环境 (venv)。")
    print("2. 您是从 'AIEducationAll/backend/' 目录下运行此脚本的。")
    print("3. 项目依赖 (包括 passlib) 已经通过 'pip install -r requirements.txt' 安装。")
    sys.exit(1)

# 您想要哈希的密码
plain_password = "student"

# 计算哈希值
try:
    hashed_password = get_password_hash(plain_password)
    print(f"密码 '{plain_password}' 的 bcrypt 哈希值是:")
    print(hashed_password)
except Exception as e:
    print(f"计算哈希时出错: {e}")
    print("请确保 passlib 已正确安装在您的虚拟环境中。")
    sys.exit(1)