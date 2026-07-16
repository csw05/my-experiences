package org.westos;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.engine.VelocityTemplateEngine;

import java.sql.*;
import java.util.Collections;

public class FastCodeGenerator {
    // 定义数据库
    public static final String MYSQL =
            "jdbc:mysql://localhost:3306/vip_system?encrypt=false&trustServerCertificate=true&useUnicode=true&characterEncoding=UTF-8&autoReconnect=true&serverTimezone=Asia/Shanghai&rewriteBatchedStatements=true";
    // 数据库用户名
    public static final String USERNAME = "root";
    // 数据库连接密码，使用你的数据密码
    public static final String PASSWORD = "123456";

    // 生成指定表代码,参数传递表名
    public static void model(String tableName) {
        // 配置数据源,三个参数在上面已经定义过了
        FastAutoGenerator.create(MYSQL, USERNAME, PASSWORD)
                // 全局配置
                .globalConfig(builder -> {
                    // 设置作者，这里随便设置,改成自己即可
                    builder.author("laoshen")
                            // 开启 swagger 模式，加入swagger 依赖，在自动生成实体类时会根据数据库中的字段注释同步添加注释
                            //.enableSwagger()
                            // 覆盖已生成文件
                            //.fileOverride()
                            // 指定输出目录，这里同步改成自己的项目路径即可，即 盘符:/文件夹/文件夹/...文件夹/项目文件夹名称/src/main/java
                            .outputDir("E:\\qiandunproject\\vip_system\\src\\main\\java");
                })
                // 包配置
                .packageConfig(builder -> {
                    // 设置父包名，这里自定义，我取名叫 "com.markerhub"
                    builder.parent("org.westos")
                            .entity("entity") //设置实体类所在的包名
                            .mapper("mapper") // 设置 Mapper 接口包名
                            .service("service") // 设置 Service 接口包名
                            .serviceImpl("service.impl") // 设置 Service 实现类包名
                            .controller("controller") // 设置 Controller 包名
                            // 设置XML生成路径，和上卖弄代码路径类似，mapper文件放置对应的 resource 文件夹中
                            .pathInfo(Collections.singletonMap(OutputFile.xml, "E:\\qiandunproject\\vip_system\\src\\main\\resources\\org\\westos\\mapper"));
                })
                // 策略配置
                .strategyConfig(builder -> {
                    // 设置需要生成的表名，有方法参数传递
                    builder.addInclude(tableName)
                            // 设置过滤表前缀，上面咱们定义的表都是 "m_"开头，如果以 "t_" 开头则对应修改即可，如果没有表前缀，不加此配置即可
                            .addTablePrefix("tb_")
                            .entityBuilder()
                            // 主键策略，自增主键嘛,不必多说
                            .idType(IdType.AUTO)
                            // 使用 Lombok，就是前面加入的Lombok插件，生成的实体类会自动加入@Getter和@Setter方法，如果还需要toString和自动逸构造器，再自行添加即可
                            //.enableLombok()
                            .mapperBuilder()
                            .enableBaseColumnList() // XML中生成基础列
                            .enableBaseResultMap() // XML中生成基础结果集
                            .serviceBuilder()
                            // 自定义 Service 文件名，即表名+Service作为业务接口类名
                            .formatServiceFileName("%sService")
                            // 自定义 Service 实现，即表名+ServiceImpl作为接口实现类名
                            .formatServiceImplFileName("%sServiceImpl")
                            .controllerBuilder()
                            // 开启 RestController 风格，自动生成的Controller控制器类会添加@RestController注解
                            .enableRestStyle();
                })
                // 模板引擎
                .templateEngine(new VelocityTemplateEngine()) // 使用 Velocity 模板引擎
                .execute();
    }

    // 优化参数，变为可变参数，为空时扫描整个数据库，不为空时根据传递的参数去生成对应的代码
    public static void generator(String... tableName) {
        // 定义数据库连接
        Connection connection = null;
        try {
            // 获取数据库连接
            connection = DriverManager.getConnection(MYSQL, USERNAME, PASSWORD);
            // 获取数据库元数据
            DatabaseMetaData metaData = connection.getMetaData();
            ResultSet tables = metaData.getTables(null, null, "%", new String[]{"TABLE"});
            // 循环可变参数生成整个数据库的代码，如果参数长度为0，说明没有人为传递表名，扫描整个数据库
            if (tableName.length == 0) {
                while (tables.next()) {
                    String table = tables.getString("TABLE_NAME");
                    model(table);
                }
                // 否则，参数长度不为0，说明人为传递了参数，因为是可变参数，管它传递了几个，直接增强for循环遍历挨个生成即可
            } else {
                for (String table : tableName) {
                    model(table);
                }
            }
            // 如果生成过程中报错，捕获异常
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args) {
        //生成一个表对应的代码调用这个方法
        // model("tb_supplier");
        //生成多个表对应的代码调用这个方法
        generator("tb_supplier", "tb_staff", "tb_goods");//为空时扫描整个数据库，不为空时根据传递的参数去生成对应的代码
    }
}

