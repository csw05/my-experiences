package org.westos;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("org.westos.mapper") //扫描该包下所有的mapper接口
public class VipSystemApplication {

    public static void main(String[] args) {
        SpringApplication.run(VipSystemApplication.class, args);
    }
}
