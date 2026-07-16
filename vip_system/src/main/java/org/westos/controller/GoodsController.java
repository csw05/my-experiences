package org.westos.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.westos.entity.Goods;
import org.westos.entity.GoodsREQ;
import org.westos.service.GoodsService;
import org.westos.utils.Result;

/**
 * <p>
 * 商品信息表 前端控制器
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@RestController
@RequestMapping("/goods")
public class GoodsController {

    //注入servcie
    @Autowired
    private GoodsService goodsService;

    /**
     * 分页条件查询商品列表
     */
    @PostMapping("/list/search/{page}/{size}")
    public Result search(@PathVariable("page") long page,
                         @PathVariable("size") long size,
                         @RequestBody(required = false) GoodsREQ req) {
        return goodsService.search(page, size, req);
    }

    //新增商品  /goods
    @PostMapping
    public Result add(@RequestBody Goods goods) {
        boolean b = goodsService.save(goods);
        if (b) {
            return Result.ok();
        }
        return Result.error("新增商品信息失败");
    }

    /**
     * 删除商品
     *
     * @return
     */
    @DeleteMapping("/{id}")
    public Result delete(@PathVariable("id") int id) {
        boolean b = goodsService.removeById(id);
        if (b) {
            return Result.ok();
        }
        return Result.error("删除商品信息失败");
    }

    /**
     * 通过id查询详情
     */
    @GetMapping("/{id}") // /goods/{id}
    public Result get(@PathVariable("id") int id) {
        return goodsService.findById(id);
    }

    /**
     * 修改商品
     */
    @PutMapping("/{id}") // /goods/{id}
    public Result update(@PathVariable("id") int id,
                         @RequestBody Goods goods) {
        return goodsService.update(id, goods);
    }
}
