package org.westos;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

@SpringBootTest
class VipSystemApplicationTests {

    @Test
    void contextLoads() {
        //$2a$10$no4onHvPyQx41GoI2/wwJu9iYvxM0L7iwkaa9R4mYp6a94QA.HrwS
        //$2a$10$QuxQgUrehA9SCiaixMZ0jeOTWaAu7ovYvD5YvFJxwoCZstgGSzrZG
        //加密，每次加完密，的密文是不一样的。
        String password = new BCryptPasswordEncoder().encode("123456");
        System.out.println(password);

        //比对
        boolean b = new BCryptPasswordEncoder().matches("123456",
                "$2a$10$no4onHvPyQx41GoI2/wwJu9iYvxM0L7iwkaa9R4mYp6a94QA.HrwS");
        System.out.println(b);

    }

}
