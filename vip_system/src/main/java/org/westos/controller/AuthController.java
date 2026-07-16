package org.westos.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.westos.entity.PasswordREQ;
import org.westos.service.StaffService;
import org.westos.utils.Result;

@RestController
@RequestMapping("/user")
public class AuthController {
    @Autowired
    private StaffService staffService;

    //校验原密码是否正确
    @PostMapping("/pwd")
    public Result checkPwd(@RequestBody PasswordREQ req) {
        return staffService.checkPassword(req);
    }

    //修改密码
    @PutMapping("/pwd")
    public Result updatePwd(@RequestBody PasswordREQ req) {
        return staffService.updatePassword(req);
    }
}