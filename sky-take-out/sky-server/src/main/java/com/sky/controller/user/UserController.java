package com.sky.controller.user;

import com.sky.entity.User;
import com.sky.mapper.UserMapper;
import com.sky.properties.JwtProperties;
import com.sky.result.Result;
import com.sky.utils.JwtUtil;
import com.sky.vo.UserLoginVO;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/user/user")
@Api(tags = "C端-用户接口")
@Slf4j
public class UserController {

    @Autowired
    private UserMapper userMapper;
    @Autowired
    private JwtProperties jwtProperties;

    @PostMapping("/login")
    @ApiOperation("微信登录")
    public Result<UserLoginVO> login(@RequestBody Map<String, String> body) {
        String code = body.get("code");
        log.info("微信用户登录，code: {}", code);

        // 因本地无微信小程序环境，使用测试用户完成登录流程验证
        // 正式环境：用 code 调微信 jscode2session 获取 openid
        User user = userMapper.getById(1L);

        Map<String, Object> claims = new HashMap<>();
        claims.put("user_id", user.getId());
        String token = JwtUtil.createJWT(
                jwtProperties.getAdminSecretKey(),
                jwtProperties.getAdminTtl(),
                claims);

        UserLoginVO vo = UserLoginVO.builder()
                .id(user.getId())
                .openid(user.getOpenid())
                .token(token)
                .build();

        log.info("登录成功，返回 token");
        return Result.success(vo);
    }
}
