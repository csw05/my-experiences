mysqldump: [Warning] Using a password on the command line interface can be insecure.
-- MySQL dump 10.13  Distrib 8.3.0, for Win64 (x86_64)
--
-- Host: localhost    Database: sky_take_out
-- ------------------------------------------------------
-- Server version	8.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `address_book`
--

DROP TABLE IF EXISTS `address_book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `address_book` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint NOT NULL COMMENT '用户id',
  `consignee` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '收货人',
  `sex` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '性别',
  `phone` varchar(11) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '手机号',
  `province_code` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '省级区划编号',
  `province_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '省级名称',
  `city_code` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '市级区划编号',
  `city_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '市级名称',
  `district_code` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '区级区划编号',
  `district_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '区级名称',
  `detail` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '详细地址',
  `label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标签',
  `is_default` tinyint(1) NOT NULL DEFAULT '0' COMMENT '默认 0 否 1是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='地址簿';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `address_book`
--

LOCK TABLES `address_book` WRITE;
/*!40000 ALTER TABLE `address_book` DISABLE KEYS */;
INSERT INTO `address_book` VALUES (2,1,'','','','','','','','','','','',0),(3,1,'张三','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'测试路1号','家',0),(4,1,'张三','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'测试路1号','家',0),(5,1,'Zhang','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'Road1','home',0),(6,1,'Zhang','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'Road1','home',0),(7,1,'Zhang','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'Road1','home',0),(8,1,'Zhang','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'Road1','home',0),(9,1,'张三','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'西安明德理工学院1栋101','学校',0),(10,1,'张三','1','13800138000',NULL,NULL,NULL,NULL,NULL,NULL,'西安明德理工学院1栋101','学校',0),(11,1,'Test','1','13900000001',NULL,NULL,NULL,NULL,NULL,NULL,'TestAddr','Home',0);
/*!40000 ALTER TABLE `address_book` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `type` int DEFAULT NULL COMMENT '类型   1 菜品分类 2 套餐分类',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '分类名称',
  `sort` int NOT NULL DEFAULT '0' COMMENT '顺序',
  `status` int DEFAULT NULL COMMENT '分类状态 0:禁用，1:启用',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `create_user` bigint DEFAULT NULL COMMENT '创建人',
  `update_user` bigint DEFAULT NULL COMMENT '修改人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_category_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='菜品及套餐分类';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (11,1,'酒水饮料',10,1,'2022-06-09 22:09:18','2022-06-09 22:09:18',1,1),(12,1,'传统主食',9,1,'2022-06-09 22:09:32','2022-06-09 22:18:53',1,1),(13,2,'人气套餐',12,1,'2022-06-09 22:11:38','2022-06-10 11:04:40',1,1),(15,2,'商务套餐',13,1,'2022-06-09 22:14:10','2022-06-10 11:04:48',1,1),(16,1,'蜀味烤鱼',4,1,'2022-06-09 22:15:37','2026-07-04 17:02:43',1,1),(17,1,'蜀味牛蛙',5,1,'2022-06-09 22:16:14','2022-08-31 14:39:44',1,1),(18,1,'特色蒸菜',6,1,'2022-06-09 22:17:42','2022-06-09 22:17:42',1,1),(19,1,'新鲜时蔬',7,1,'2022-06-09 22:18:12','2022-06-09 22:18:28',1,1),(20,1,'水煮鱼',8,1,'2022-06-09 22:22:29','2022-06-09 22:23:45',1,1),(21,1,'汤类',11,1,'2022-06-10 10:51:47','2022-06-10 10:51:47',1,1);
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dish`
--

DROP TABLE IF EXISTS `dish`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dish` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '菜品名称',
  `category_id` bigint NOT NULL COMMENT '菜品分类id',
  `price` decimal(10,2) DEFAULT NULL COMMENT '菜品价格',
  `image` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '图片',
  `description` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '描述信息',
  `status` int DEFAULT '1' COMMENT '0 停售 1 起售',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `create_user` bigint DEFAULT NULL COMMENT '创建人',
  `update_user` bigint DEFAULT NULL COMMENT '修改人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_dish_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='菜品';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dish`
--

LOCK TABLES `dish` WRITE;
/*!40000 ALTER TABLE `dish` DISABLE KEYS */;
INSERT INTO `dish` VALUES (46,'王老吉',11,6.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/44fb3a23-96d3-4456-8428-643e000ac5b3.jpeg','',1,'2022-06-09 22:40:47','2026-07-04 16:38:02',1,1),(47,'北冰洋',11,4.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/35bec1f6-189f-4493-838c-3251fe081070.jpeg','还是小时候的味道',1,'2022-06-10 09:18:49','2026-07-04 16:37:46',1,1),(48,'雪花啤酒',11,4.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/6ec58100-8d4f-4fb1-a773-06ea1532af33.jpeg','',1,'2022-06-10 09:22:54','2026-07-04 16:28:02',1,1),(49,'米饭',12,2.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/139309bc-747e-471c-b81b-4eb808f71a8e.jpeg','精选五常大米',1,'2022-06-10 09:30:17','2026-07-04 16:27:25',1,1),(50,'馒头',12,1.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/7d266207-cbb3-4975-a7f7-b05b6b3a9106.jpeg','优质面粉',1,'2022-06-10 09:34:28','2026-07-04 16:27:46',1,1),(51,'老坛酸菜鱼',20,56.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/e793bf4f-f1c8-4acb-bb2a-6850aeb09930.jpeg','原料：汤，草鱼，酸菜',1,'2022-06-10 09:40:51','2026-07-04 16:19:47',1,1),(52,'经典酸菜鮰鱼',20,66.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/5215ec5f-4240-4516-8a24-fdd744c5a58b.jpeg','原料：酸菜，江团，鮰鱼',1,'2022-06-10 09:46:02','2026-07-04 16:24:18',1,1),(53,'蜀味水煮草鱼',20,38.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/b98dba13-cb90-45fa-97bd-097ecb3838e6.jpeg','原料：草鱼，汤',1,'2022-06-10 09:48:37','2026-07-04 16:25:08',1,1),(54,'清炒小油菜',19,18.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/5f12c265-099c-4d9e-a3ac-868944130688.jpeg','原料：小油菜',1,'2022-06-10 09:51:46','2026-07-04 16:20:19',1,1),(55,'蒜蓉娃娃菜',19,18.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/7447513a-d3e4-4bc9-9b55-3d226b4d3ca9.jpeg','原料：蒜，娃娃菜',1,'2022-06-10 09:53:37','2026-07-04 16:37:08',1,1),(56,'清炒西兰花',19,18.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/ebe7672f-b30a-4826-8d22-e1d4e6f2cd36.jpeg','原料：西兰花',1,'2022-06-10 09:55:44','2026-07-04 16:36:52',1,1),(57,'炝炒圆白菜',19,18.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/915d164b-a104-4cdf-99ea-3674626b582e.jpeg','原料：圆白菜',1,'2022-06-10 09:58:35','2026-07-04 16:35:37',1,1),(58,'清蒸鲈鱼',18,98.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/3c168833-63e4-4a95-9351-2f88db40697f.jpeg','原料：鲈鱼',1,'2022-06-10 10:12:28','2026-07-04 16:26:05',1,1),(59,'东坡肘子',18,138.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/ab920a63-8101-4cb7-8f44-197b9c33399f.jpeg','原料：猪肘棒',1,'2022-06-10 10:24:03','2026-07-04 16:26:31',1,1),(60,'梅菜扣肉',18,58.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/f6f48798-d301-407d-aae0-4140e2bfbf39.jpeg','原料：猪肉，梅菜',1,'2022-06-10 10:26:03','2026-07-04 16:25:29',1,1),(61,'剁椒鱼头',18,66.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/e3aeaa18-802c-4959-a58d-1bf810666ef4.jpeg','原料：鲢鱼，剁椒',1,'2022-06-10 10:28:54','2026-07-04 16:34:17',1,1),(62,'金汤酸菜牛蛙',17,88.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/963d1743-e87d-4a59-83d6-b78f71fa5737.jpeg','原料：鲜活牛蛙，酸菜',1,'2022-06-10 10:33:05','2026-07-04 16:33:51',1,1),(63,'香锅牛蛙',17,88.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/168382a5-bcc6-4e6b-81da-9dce7de05b9e.jpeg','配料：鲜活牛蛙，莲藕，青笋',1,'2022-06-10 10:35:40','2026-07-04 16:33:40',1,1),(64,'馋嘴牛蛙',17,88.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/3e47be8e-b1a7-4ab9-affb-53259339d180.jpeg','配料：鲜活牛蛙，丝瓜，黄豆芽',1,'2022-06-10 10:37:52','2026-07-04 16:33:25',1,1),(65,'草鱼2斤',16,68.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/53e3477c-63ff-4e85-9dc7-f9e8159eae81.jpeg','原料：草鱼，黄豆芽，莲藕',1,'2022-06-10 10:41:08','2026-07-04 16:32:16',1,1),(66,'江团鱼2斤',16,119.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/d4d965e9-cea8-454e-864c-257279f6d1be.jpeg','配料：江团鱼，黄豆芽，莲藕',1,'2022-06-10 10:42:42','2026-07-04 16:31:57',1,1),(67,'鮰鱼2斤',16,72.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/47f0a231-a663-402a-adf3-a079adaba488.jpeg','原料：鮰鱼，黄豆芽，莲藕',1,'2022-06-10 10:43:56','2026-07-06 16:45:25',1,1),(68,'鸡蛋汤',21,4.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/f0951654-6f75-4efc-bfcb-18460b0b942b.jpeg','配料：鸡蛋，紫菜',1,'2022-06-10 10:54:25','2026-07-06 16:45:13',1,1),(69,'平菇豆腐汤',21,6.00,'https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/801fa973-1d08-43b6-973a-be467765d81b.jpeg','配料：豆腐，平菇',1,'2022-06-10 10:55:02','2026-07-06 16:45:06',1,1);
/*!40000 ALTER TABLE `dish` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dish_flavor`
--

DROP TABLE IF EXISTS `dish_flavor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dish_flavor` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `dish_id` bigint NOT NULL COMMENT '菜品',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '口味名称',
  `value` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '口味数据list',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='菜品口味关系表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dish_flavor`
--

LOCK TABLES `dish_flavor` WRITE;
/*!40000 ALTER TABLE `dish_flavor` DISABLE KEYS */;
INSERT INTO `dish_flavor` VALUES (40,10,'甜味','[\"无糖\",\"少糖\",\"半糖\",\"多糖\",\"全糖\"]'),(41,7,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(42,7,'温度','[\"热饮\",\"常温\",\"去冰\",\"少冰\",\"多冰\"]'),(45,6,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(46,6,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]'),(47,5,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]'),(48,5,'甜味','[\"无糖\",\"少糖\",\"半糖\",\"多糖\",\"全糖\"]'),(49,2,'甜味','[\"无糖\",\"少糖\",\"半糖\",\"多糖\",\"全糖\"]'),(50,4,'甜味','[\"无糖\",\"少糖\",\"半糖\",\"多糖\",\"全糖\"]'),(51,3,'甜味','[\"无糖\",\"少糖\",\"半糖\",\"多糖\",\"全糖\"]'),(52,3,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(113,51,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(114,51,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]'),(115,54,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\"]'),(116,52,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(117,52,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]'),(118,53,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(119,53,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]'),(120,60,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(122,66,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]'),(123,65,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]'),(124,57,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(125,56,'忌口','[\"不要葱\",\"不要蒜\",\"不要香菜\",\"不要辣\"]'),(126,67,'辣度','[\"不辣\",\"微辣\",\"中辣\",\"重辣\"]');
/*!40000 ALTER TABLE `dish_flavor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employee`
--

DROP TABLE IF EXISTS `employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '姓名',
  `username` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '用户名',
  `password` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '密码',
  `phone` varchar(11) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '手机号',
  `sex` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '性别',
  `id_number` varchar(18) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '身份证号',
  `status` int NOT NULL DEFAULT '1' COMMENT '状态 0:禁用，1:启用',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `create_user` bigint DEFAULT NULL COMMENT '创建人',
  `update_user` bigint DEFAULT NULL COMMENT '修改人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='员工信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee`
--

LOCK TABLES `employee` WRITE;
/*!40000 ALTER TABLE `employee` DISABLE KEYS */;
INSERT INTO `employee` VALUES (1,'管理员','admin','e10adc3949ba59abbe56e057f20f883e','13812312312','1','110101199001010047',1,'2022-02-15 15:51:20','2022-02-17 09:16:20',10,1),(2,'李四','1231541','e10adc3949ba59abbe56e057f20f883e','13106069057','1','123103482479548',1,'2026-07-02 15:06:47','2026-07-03 16:38:27',10,1);
/*!40000 ALTER TABLE `employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_detail`
--

DROP TABLE IF EXISTS `order_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '名字',
  `image` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '图片',
  `order_id` bigint NOT NULL COMMENT '订单id',
  `dish_id` bigint DEFAULT NULL COMMENT '菜品id',
  `setmeal_id` bigint DEFAULT NULL COMMENT '套餐id',
  `dish_flavor` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '口味',
  `number` int NOT NULL DEFAULT '1' COMMENT '数量',
  `amount` decimal(10,2) NOT NULL COMMENT '金额',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='订单明细表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_detail`
--

LOCK TABLES `order_detail` WRITE;
/*!40000 ALTER TABLE `order_detail` DISABLE KEYS */;
INSERT INTO `order_detail` VALUES (5,'王老吉','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/44fb3a23-96d3-4456-8428-643e000ac5b3.jpeg',4,46,NULL,'常温',8,6.00),(6,'雪花啤酒套餐','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/a1090f0c-3dcc-406f-a102-549ff586adcf.png',4,NULL,32,NULL,1,45.00),(7,'王老吉','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/44fb3a23-96d3-4456-8428-643e000ac5b3.jpeg',5,46,NULL,NULL,2,6.00),(8,'王老吉','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/44fb3a23-96d3-4456-8428-643e000ac5b3.jpeg',6,46,NULL,NULL,1,6.00),(9,'王老吉','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/44fb3a23-96d3-4456-8428-643e000ac5b3.jpeg',7,46,NULL,NULL,1,6.00),(10,'王老吉','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/44fb3a23-96d3-4456-8428-643e000ac5b3.jpeg',8,46,NULL,NULL,1,6.00),(11,'老坛酸菜鱼','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/e793bf4f-f1c8-4acb-bb2a-6850aeb09930.jpeg',8,51,NULL,NULL,1,56.00),(12,'经典酸菜鮰鱼','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/5215ec5f-4240-4516-8a24-fdd744c5a58b.jpeg',8,52,NULL,NULL,1,66.00),(13,'经典酸菜鮰鱼','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/5215ec5f-4240-4516-8a24-fdd744c5a58b.jpeg',9,52,NULL,NULL,1,66.00),(14,'老坛酸菜鱼','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/e793bf4f-f1c8-4acb-bb2a-6850aeb09930.jpeg',10,51,NULL,NULL,1,56.00),(15,'蜀味水煮草鱼','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/b98dba13-cb90-45fa-97bd-097ecb3838e6.jpeg',11,53,NULL,NULL,1,38.00);
/*!40000 ALTER TABLE `order_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `number` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '订单号',
  `status` int NOT NULL DEFAULT '1' COMMENT '订单状态 1待付款 2待接单 3已接单 4派送中 5已完成 6已取消 7退款',
  `user_id` bigint NOT NULL COMMENT '下单用户',
  `address_book_id` bigint NOT NULL COMMENT '地址id',
  `order_time` datetime NOT NULL COMMENT '下单时间',
  `checkout_time` datetime DEFAULT NULL COMMENT '结账时间',
  `pay_method` int NOT NULL DEFAULT '1' COMMENT '支付方式 1微信,2支付宝',
  `pay_status` tinyint NOT NULL DEFAULT '0' COMMENT '支付状态 0未支付 1已支付 2退款',
  `amount` decimal(10,2) NOT NULL COMMENT '实收金额',
  `remark` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '备注',
  `phone` varchar(11) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '手机号',
  `address` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '地址',
  `user_name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '用户名称',
  `consignee` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '收货人',
  `cancel_reason` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '订单取消原因',
  `rejection_reason` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '订单拒绝原因',
  `cancel_time` datetime DEFAULT NULL COMMENT '订单取消时间',
  `estimated_delivery_time` datetime DEFAULT NULL COMMENT '预计送达时间',
  `delivery_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '配送状态  1立即送出  0选择具体时间',
  `delivery_time` datetime DEFAULT NULL COMMENT '送达时间',
  `pack_amount` int DEFAULT NULL COMMENT '打包费',
  `tableware_number` int DEFAULT NULL COMMENT '餐具数量',
  `tableware_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '餐具数量状态  1按餐量提供  0选择具体数量',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='订单表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (4,'1783395305147',5,1,6,'2026-07-06 18:00:00',NULL,1,0,99.00,NULL,'13800138000','Road1',NULL,'Zhang','支付超时，自动取消',NULL,'2026-07-07 14:36:00',NULL,1,NULL,1,1,1),(5,'1783406758718',5,1,6,'2026-07-06 15:00:00',NULL,1,0,99.00,NULL,'13800138000','Road1',NULL,'Zhang','支付超时，自动取消',NULL,'2026-07-07 15:01:00',NULL,1,NULL,1,1,1),(6,'1783406998670',5,1,8,'2026-07-05 10:00:00',NULL,1,0,99.00,NULL,'13800138000','Road1',NULL,'Zhang','支付超时，自动取消',NULL,'2026-07-07 15:05:00',NULL,1,'2026-07-07 15:23:16',1,1,1),(7,'1783407418717',3,1,8,'2026-07-06 09:00:00',NULL,1,0,99.00,NULL,'13800138000','Road1',NULL,'Zhang','支付超时，自动取消',NULL,'2026-07-07 15:12:00',NULL,1,NULL,1,1,1),(8,'1783409195808',5,1,8,'2026-07-01 11:00:00',NULL,1,0,128.00,NULL,'13800138000','Road1',NULL,'Zhang',NULL,NULL,NULL,NULL,1,NULL,2,1,1),(9,'1783409204478',5,1,8,'2026-07-02 12:30:00',NULL,1,0,68.00,NULL,'13800138000','Road1',NULL,'Zhang',NULL,NULL,NULL,NULL,1,NULL,1,1,1),(10,'1783409204578',5,1,8,'2026-07-03 13:00:00',NULL,1,0,58.00,NULL,'13800138000','Road1',NULL,'Zhang',NULL,NULL,NULL,NULL,1,NULL,1,1,1),(11,'1783409204691',4,1,8,'2026-07-04 14:00:00',NULL,1,0,40.00,NULL,'13800138000','Road1',NULL,'Zhang',NULL,NULL,NULL,NULL,1,NULL,1,1,1);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `setmeal`
--

DROP TABLE IF EXISTS `setmeal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `setmeal` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `category_id` bigint NOT NULL COMMENT '菜品分类id',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '套餐名称',
  `price` decimal(10,2) NOT NULL COMMENT '套餐价格',
  `status` int DEFAULT '1' COMMENT '售卖状态 0:停售 1:起售',
  `description` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '描述信息',
  `image` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '图片',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `create_user` bigint DEFAULT NULL COMMENT '创建人',
  `update_user` bigint DEFAULT NULL COMMENT '修改人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_setmeal_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='套餐';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setmeal`
--

LOCK TABLES `setmeal` WRITE;
/*!40000 ALTER TABLE `setmeal` DISABLE KEYS */;
INSERT INTO `setmeal` VALUES (32,13,'雪花啤酒套餐',45.00,1,'雪花啤酒x12！','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/a1090f0c-3dcc-406f-a102-549ff586adcf.png',NULL,NULL,NULL,NULL),(33,13,'牛蛙套餐',240.00,1,'三种口味任你挑！','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/dd905174-d4f8-4be6-888b-bc8e362d41e7.jpeg',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `setmeal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `setmeal_dish`
--

DROP TABLE IF EXISTS `setmeal_dish`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `setmeal_dish` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `setmeal_id` bigint DEFAULT NULL COMMENT '套餐id',
  `dish_id` bigint DEFAULT NULL COMMENT '菜品id',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '菜品名称 （冗余字段）',
  `price` decimal(10,2) DEFAULT NULL COMMENT '菜品单价（冗余字段）',
  `copies` int DEFAULT NULL COMMENT '菜品份数',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='套餐菜品关系';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setmeal_dish`
--

LOCK TABLES `setmeal_dish` WRITE;
/*!40000 ALTER TABLE `setmeal_dish` DISABLE KEYS */;
INSERT INTO `setmeal_dish` VALUES (47,32,48,'雪花啤酒',4.00,12),(48,33,62,'金汤酸菜牛蛙',88.00,1),(49,33,63,'香锅牛蛙',88.00,1),(50,33,64,'馋嘴牛蛙',88.00,1);
/*!40000 ALTER TABLE `setmeal_dish` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shopping_cart`
--

DROP TABLE IF EXISTS `shopping_cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shopping_cart` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '商品名称',
  `image` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '图片',
  `user_id` bigint NOT NULL COMMENT '主键',
  `dish_id` bigint DEFAULT NULL COMMENT '菜品id',
  `setmeal_id` bigint DEFAULT NULL COMMENT '套餐id',
  `dish_flavor` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '口味',
  `number` int NOT NULL DEFAULT '1' COMMENT '数量',
  `amount` decimal(10,2) NOT NULL COMMENT '金额',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='购物车';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shopping_cart`
--

LOCK TABLES `shopping_cart` WRITE;
/*!40000 ALTER TABLE `shopping_cart` DISABLE KEYS */;
INSERT INTO `shopping_cart` VALUES (23,'王老吉','https://sky-take-out-csw1.oss-cn-hangzhou.aliyuncs.com/44fb3a23-96d3-4456-8428-643e000ac5b3.jpeg',1,46,NULL,NULL,2,6.00,'2026-07-09 15:10:47');
/*!40000 ALTER TABLE `shopping_cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `openid` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '微信用户唯一标识',
  `name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '姓名',
  `phone` varchar(11) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '手机号',
  `sex` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '性别',
  `id_number` varchar(18) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '身份证号',
  `avatar` varchar(500) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL COMMENT '头像',
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='用户信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'test_openid_001','测试用户',NULL,NULL,NULL,NULL,'2026-07-07 10:10:29'),(4,'wx_001','用户A',NULL,NULL,NULL,NULL,'2026-07-01 08:00:00'),(5,'wx_002','用户B',NULL,NULL,NULL,NULL,'2026-07-01 10:00:00'),(6,'wx_003','用户C',NULL,NULL,NULL,NULL,'2026-07-02 09:00:00'),(7,'wx_004','用户D',NULL,NULL,NULL,NULL,'2026-07-03 08:00:00'),(8,'wx_005','用户E',NULL,NULL,NULL,NULL,'2026-07-03 11:00:00'),(9,'wx_006','用户F',NULL,NULL,NULL,NULL,'2026-07-03 14:00:00'),(10,'wx_007','用户G',NULL,NULL,NULL,NULL,'2026-07-05 08:00:00'),(11,'wx_008','用户H',NULL,NULL,NULL,NULL,'2026-07-05 15:00:00'),(12,'wx_009','用户I',NULL,NULL,NULL,NULL,'2026-07-06 09:00:00');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-12 16:46:35
