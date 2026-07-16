# VIP 会员管理系统

Spring Boot 3 + MyBatis-Plus + Vue 3 + Element Plus 全栈会员管理后台。

## 功能模块

| 模块 | 功能 |
|------|------|
| 会员管理 | 会员信息 CRUD、分页搜索、积分/余额管理 |
| 商品管理 | 商品 CRUD、库存管理、供应商关联 |
| 员工管理 | 员工账号管理、BCrypt 密码加密 |
| 供应商管理 | 供应商信息维护 |

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Spring Boot 3.4、MyBatis-Plus 3.5、Druid、Spring Security Crypto |
| 数据库 | MySQL 8.0 |
| 前端 | Vue 3、Element Plus、Axios（零 CDN，全部本地化） |

## 快速开始

### 环境要求

- JDK 17+
- MySQL 8.0+
- Maven 3.6+

### 1. 初始化数据库

```bash
mysql -uroot -p < init.sql
```

### 2. 修改数据库配置

编辑 `src/main/resources/application.properties`，修改数据库用户名和密码：

```properties
spring.datasource.username=root
spring.datasource.password=你的密码
```

### 3. 启动后端

```bash
mvnw spring-boot:run
```

或编译后运行：

```bash
mvnw clean package -DskipTests
java -jar target/vip_system-0.0.1-SNAPSHOT.jar
```

### 4. 访问系统

浏览器打开 `http://localhost:9999/index.html`

**默认账号**: `admin` / `123456`

## 项目结构

```
├── init.sql                 # 数据库初始化脚本（含默认管理员）
├── pom.xml                  # Maven 配置
├── src/
│   └── main/
│       ├── java/org/westos/
│       │   ├── controller/  # REST API 控制器
│       │   ├── entity/      # 实体类
│       │   ├── mapper/      # MyBatis Mapper
│       │   ├── service/     # 业务逻辑
│       │   └── utils/       # 工具类
│       └── resources/
│           ├── application.properties
│           └── static/      # 前端静态资源
│               ├── index.html     # 登录页
│               ├── main.html      # 管理后台
│               ├── css/style.css  # 样式
│               ├── js/api.js      # API 封装
│               └── lib/           # Vue/Element+/Axios（本地化）
```

## API 接口

所有接口返回统一格式：

```json
{ "code": 2000, "flag": true, "message": "成功", "data": {} }
```

| 路径 | 方法 | 说明 |
|------|------|------|
| `/user/pwd` | POST | 校验密码 |
| `/user/pwd` | PUT | 修改密码 |
| `/member/list/search/{page}/{size}` | POST | 分页查询会员 |
| `/member` | POST/GET/PUT/DELETE | 会员 CRUD |
| `/goods/list/search/{page}/{size}` | POST | 分页查询商品 |
| `/goods` | POST/GET/PUT/DELETE | 商品 CRUD |
| `/staff/list/search/{page}/{size}` | POST | 分页查询员工 |
| `/staff` | POST/GET/PUT/DELETE | 员工 CRUD |
| `/supplier/list/search/{page}/{size}` | POST | 分页查询供应商 |
| `/supplier` | POST/GET/PUT/DELETE | 供应商 CRUD |
