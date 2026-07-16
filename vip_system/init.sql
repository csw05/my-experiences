-- VIP系统数据库初始化脚本
CREATE DATABASE IF NOT EXISTS vip_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE vip_system;

-- 会员表
CREATE TABLE IF NOT EXISTS tb_member (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    card_num VARCHAR(50) COMMENT '会员卡号',
    name VARCHAR(50) COMMENT '会员名字',
    birthday DATE COMMENT '生日',
    phone VARCHAR(20) COMMENT '手机号',
    integral INT DEFAULT 0 COMMENT '可用积分',
    money DOUBLE DEFAULT 0 COMMENT '可用金额',
    pay_type VARCHAR(10) COMMENT '支付类型(1现金,2微信,3支付宝,4银行卡)',
    address VARCHAR(200) COMMENT '会员地址'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员信息表';

-- 供应商表
CREATE TABLE IF NOT EXISTS tb_supplier (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    name VARCHAR(100) COMMENT '供应商名称',
    linkman VARCHAR(50) COMMENT '联系人',
    mobile VARCHAR(20) COMMENT '联系电话',
    remark VARCHAR(500) COMMENT '备注'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商信息表';

-- 商品表
CREATE TABLE IF NOT EXISTS tb_goods (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    name VARCHAR(100) COMMENT '商品名称',
    code VARCHAR(50) COMMENT '商品编码',
    spec VARCHAR(100) COMMENT '商品规格',
    retail_price DECIMAL(10, 2) COMMENT '零售价',
    purchase_price DECIMAL(10, 2) COMMENT '进货价',
    storage_num INT DEFAULT 0 COMMENT '库存数量',
    supplier_id INT COMMENT '供应商id'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品信息表';

-- 员工表
CREATE TABLE IF NOT EXISTS tb_staff (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL COMMENT '帐号',
    password VARCHAR(200) NOT NULL COMMENT '密码',
    name VARCHAR(50) COMMENT '姓名',
    age INT COMMENT '年龄',
    mobile VARCHAR(20) COMMENT '电话',
    salary DECIMAL(10, 2) COMMENT '薪酬',
    entry_date DATE COMMENT '入职时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='员工信息表';

-- 默认管理员账号 (密码: 123456, BCrypt加密)
INSERT INTO tb_staff (username, password, name, age, mobile, salary, entry_date) VALUES
('admin', '$2b$12$ezl69/AbGVfytqtMM7PP2uAvFnCFi0dW5PfFImJZe5ZkM6eaCZ9fa', 'Admin', 25, '13800000000', 8000.00, '2024-01-01');
