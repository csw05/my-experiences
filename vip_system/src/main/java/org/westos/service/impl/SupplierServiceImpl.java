package org.westos.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.apache.commons.lang.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.westos.entity.Goods;
import org.westos.entity.Supplier;
import org.westos.entity.SupplierREQ;
import org.westos.mapper.SupplierMapper;
import org.westos.service.GoodsService;
import org.westos.service.SupplierService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import org.westos.utils.Result;

import java.util.List;

/**
 * <p>
 * 供应商信息表 服务实现类
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@Service
public class SupplierServiceImpl extends ServiceImpl<SupplierMapper, Supplier> implements SupplierService {
    @Autowired
    private GoodsService goodsService; //注入商品的业务层对象

    @Override
    public Result search(long page, long size, SupplierREQ req) {
        //创建拼接查询条件的对象
        QueryWrapper<Supplier> queryWrapper = new QueryWrapper<>();
        if (req != null) {
            if (StringUtils.isNotBlank(req.getName())) {
                queryWrapper.like("name", req.getName());
            }
            if (StringUtils.isNotBlank(req.getLinkman())) {
                queryWrapper.like("linkman", req.getLinkman());
            }
            if (StringUtils.isNotBlank(req.getMobile())) {
                queryWrapper.like("mobile", req.getMobile());
            }
        }
        //创建分页信息对象
        Page<Supplier> supplierPage = new Page<>(page, size);
        //分页条件查询
        baseMapper.selectPage(supplierPage, queryWrapper);
        return Result.ok(supplierPage);
    }

    //删除供应商的方法
    @Override
    public Result deleteById(int id) {
        // 1. 通过供应商id查询是否被商品引用，
        List<Goods> goodsList = goodsService.selectBySupplierId(id);
        // 2. 如果被商品引用，则不让删除供应商
        if (goodsList != null && goodsList.size() > 0) {
            return Result.error("该供应商被商品引用，不允许删除");
        }
        // 3. 如果没有被引用，直接删除
        int i = baseMapper.deleteById(id);
        if (i < 1) {
            return Result.error("删除供应商失败");
        }
        return Result.ok();
    }

    //修改供应商的方法
    @Override
    public Result update(int id, Supplier supplier) {
        if (supplier.getId() == null) {
            supplier.setId(id);
        }
        //更新操作
        int size = baseMapper.updateById(supplier);
        if (size < 1) {
            return Result.error("修改供应商信息失败");
        }
        return Result.ok();
    }
}
