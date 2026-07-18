# 苍穹外卖 (Sky Take-Out)

餐饮 O2O 外卖平台后端系统

## 技术栈

Spring Boot 2.7 + MyBatis-Plus + MySQL + Redis + 阿里云 OSS + JWT + WebSocket

## 项目结构

```
cangqiongwaimai/
├── sky-take-out/          # 后端 Spring Boot 项目
│   ├── sky-common/        # 公共模块（常量、工具类、属性配置）
│   ├── sky-pojo/          # 实体模块（Entity、DTO、VO）
│   └── sky-server/        # 服务模块（Controller、Service、Mapper）
├── sky_take_out.sql       # 数据库初始化脚本
├── front-environment/     # 前端部署文件（Nginx 静态资源）
└── wx-miniprograme/       # 微信小程序源码
```

## 环境要求

- JDK 21+
- MySQL 8.0+
- Redis（Windows 版）
- Maven 3.6+
- Nginx（用于前端部署）
- 微信开发者工具（[下载](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)）

## 快速开始

1. 导入 `sky_take_out.sql` 到 MySQL
2. 修改 `sky-server/src/main/resources/application-dev.yml` 中的数据库/Redis/OSS/微信配置
3. `cd sky-take-out && mvn clean install -DskipTests`
4. 启动 `sky-server` 主类
5. 将 `front-environment/` 部署到 Nginx
