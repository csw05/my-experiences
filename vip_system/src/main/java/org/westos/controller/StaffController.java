package org.westos.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.westos.entity.Staff;
import org.westos.entity.StaffREQ;
import org.westos.service.StaffService;
import org.westos.utils.Result;

/**
 * <p>
 * 员工信息表 前端控制器
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@RestController
@RequestMapping("/staff")
public class StaffController {
    @Autowired // 注入servicc
    private StaffService staffService;

    /**
     * 分页条件查询员工列表
     */
    @PostMapping("/list/search/{page}/{size}")
    public Result search(@PathVariable("page") long page,
                         @PathVariable("size") long size,
                         @RequestBody(required = false) StaffREQ req) {
        return staffService.search(page, size, req);
    }

    //新增
    @PostMapping // /staff
    public Result add(@RequestBody Staff staff) {
        return staffService.add(staff);
    }

    //根据id删除
    @DeleteMapping("/{id}")
    public Result delete(@PathVariable("id") int id) {
        boolean b = staffService.removeById(id); //直接调用IStaffService 接口中提供的方法
        if (b) {
            return Result.ok();
        }
        return Result.error("删除员工信息失败");
    }

    //通过id查询员工详情
    @GetMapping("/{id}") // /staff/{id}
    public Result get(@PathVariable("id") int id) {
        Staff staff = staffService.getById(id);
        return Result.ok(staff);
    }

    //修改员工
    @PutMapping("/{id}") // /staff/{id}
    public Result update(@PathVariable("id") int id,
                         @RequestBody Staff staff) {
        return staffService.update(id, staff);
    }
}
