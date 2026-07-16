package org.westos.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Service;
import org.westos.entity.Goods;
import org.westos.entity.GoodsREQ;
import org.westos.entity.Supplier;
import org.westos.mapper.GoodsMapper;
import org.westos.service.GoodsService;
import org.westos.service.SupplierService;
import org.westos.utils.Result;

import java.util.List;

/**
 * <p>
 * 商品信息表 服务实现类
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@Service
public class GoodsServiceImpl extends ServiceImpl<GoodsMapper, Goods> implements GoodsService {
    //这里不要用 @Autowired 来注入SupplierService，因为有循环依赖问题，因为我们之前在 SupplierService注入过GoodsService
    //你要在GoodsService里面通过@Autowired 来注入SupplierService 就会有循环依赖的问题，启动就会报错，因为在Spring6对循环依赖检查比较严格，
    //解决方法：在构造函数里面使用@Lazy注解，告诉Spring这个类是延迟加载的，不会在启动的时候就创建对象，而是使用时才创建对象
    private SupplierService supplierService;

    //提供构造函数，将SupplierService注入到GoodsServiceImpl中，这里延迟注入。
    public GoodsServiceImpl(@Lazy SupplierService supplierService) {
        this.supplierService = supplierService;
    }

    @Override
    public List<Goods> selectBySupplierId(int supplierId) {
        QueryWrapper<Goods> query = new QueryWrapper<>();
        query.eq("supplier_id", supplierId);
        return baseMapper.selectList(query);
    }

    @Override
    public Result search(long page, long size, GoodsREQ req) {
        //防止前台没有传递req 那我们就创建一个，防止空指针
        if (req == null) {
            req = new GoodsREQ();
        }
        // 在 GoodsMapper 已经实现了 searchPage 分页条件查询
        IPage<Goods> data = baseMapper.searchPage(new Page<Goods>(page, size), req);
        return Result.ok(data);
    }

    @Override
    public Result findById(int id) {
        // 通过商品的id 查询商品详情
        Goods goods = baseMapper.selectById(id);
        // 从商品中取出 supplierId 然后去查查询供应商名称，设置到商品对象中
        if (goods != null && goods.getSupplierId() != null) {
            Supplier supplier = supplierService.getById(goods.getSupplierId());
            if (supplier != null) {
                //供应商名称，设置到商品对象中
                goods.setSupplierName(supplier.getName());
            }
        }

        return Result.ok(goods);
    }

    @Override
    public Result update(int id, Goods goods) {
        if (goods.getId() == null) {
            goods.setId(id);
        }
        //更新操作
        int size = baseMapper.updateById(goods);
        if (size < 1) {
            return Result.error("修改商品信息失败");
        }
        return Result.ok();
    }
}
