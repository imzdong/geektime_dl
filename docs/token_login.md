# Token登录功能说明

## 概述

geektime_dl现在支持两种登录方式：
1. **传统登录**：手机号 + 密码
2. **Token登录**：直接使用认证token

## Token登录的优势

- **更安全**：不需要在配置文件中保存明文密码
- **更便捷**：一次获取token，长期使用
- **更稳定**：避免了频繁登录导致的封号风险

## 获取Token

### 方法一：使用工具脚本

```bash
cd /Users/admin/CodeBuddy/geektime_dl
python utils/get_token.py --help
```

### 方法二：手动获取

1. 在浏览器中登录极客时间网站
2. 按F12打开开发者工具
3. 切换到Network标签
4. 刷新页面，找到任意API请求
5. 在请求头中找到Cookie字段，复制完整值

## 使用Token登录

### 方式一：命令行直接登录

```bash
# 使用完整Cookie字符串
geektime login --auth-type token --auth-token "your_complete_cookie_string"

# 使用单个token（如果知道具体的token名）
geektime login --auth-type token --auth-token "your_jwt_token"
```

### 方式二：配置文件

创建 `geektime.cfg` 文件：

```ini
[default]
auth_type = token
auth_token = your_token_here
output_folder = ./output
```

## 配置示例

参考 `geektime.cfg.example` 文件：

```ini
# Token登录示例
[default]
auth_type = token
auth_token = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
output_folder = ./output

# 传统登录示例（注释掉）
# [default]
# auth_type = password
# account = 13800138000
# password = your_password
# area = 86
# output_folder = ./output
```

## Token格式支持

支持多种token格式：

### 1. JWT Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### 2. Cookie字符串
```
GCLOUD=jwt_token_value; GCESS=another_value; SERVERID=session_id
```

### 3. 单个Token
```
GCLOUD_SESSION_123456789
```

## 测试功能

运行测试脚本验证功能：

```bash
cd /Users/admin/CodeBuddy/geektime_dl
python test_token_login.py
```

## 常见问题

### Q: Token过期了怎么办？
A: 重新获取token并更新配置文件，或者重新运行登录命令。

### Q: Token登录失败？
A: 检查token格式是否正确，是否包含完整的认证信息。

### Q: 如何切换回密码登录？
A: 修改配置文件中的 `auth_type = password`，或者使用账号密码参数登录。

## 技术实现

Token登录通过以下方式实现：

1. **JWT Token**：在请求头中添加 `Authorization: Bearer <token>`
2. **Cookie Token**：将token解析并设置为HTTP cookies
3. **自动检测**：根据token格式自动选择合适的认证方式

## 安全建议

1. 不要在公共场合分享你的token
2. 定期更换token以提高安全性
3. 配置文件权限设置为只读：`chmod 400 geektime.cfg`
4. 使用配置文件时避免token出现在命令行历史中