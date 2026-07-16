package org.westos.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.westos.entity.Supplier;
import org.westos.entity.SupplierREQ;
import org.westos.service.SupplierService;
import org.westos.utils.Result;

/**
 * <p>
 * 供应商信息表 前端控制器
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@RestController
@RequestMapping("/supplier")
public class SupplierController {
    @Autowired // 不要少了注解
    private SupplierService supplierService;

    /**
     * 分页条件查询供应商列表
     *
     * @param page 页码
     * @param size 每页显示记录数
     * @param req  查询条件
     * @return
     */
    @PostMapping("/list/search/{page}/{size}")
    public Result search(@PathVariable("page") long page,
                         @PathVariable("size") long size,
                         @RequestBody(required = false) SupplierREQ req) {
        return supplierService.search(page, size, req);
    }

    //新增的方法
    @PostMapping // /supplier
    public Result add(@RequestBody Supplier supplier) {
        boolean b = supplierService.save(supplier);
        if (b) {
            return Result.ok();
        }
        return Result.error("新增供应商信息失败");
    }

    //删除的方法
    @DeleteMapping("/{id}")
    public Result delete(@PathVariable("id") int id) {
        return supplierService.deleteById(id);
    }

    /**
     * 通过id查询供应商
     */
    @GetMapping("/{id}") // /supplier/{id}
    public Result get(@PathVariable("id") int id) {
        Supplier supplier = supplierService.getById(id);
        if (supplier != null) {
            return Result.ok("查询供应商成功", supplier);
        }
        return Result.error("查询供应商信息失败！");
    }

    /**
     * 修改供应商
     */
    @PutMapping("/{id}") // /supplier/{id}
    public Result update(@PathVariable("id") int id, @RequestBody Supplier supplier) {
        return supplierService.update(id, supplier);
    }
}
