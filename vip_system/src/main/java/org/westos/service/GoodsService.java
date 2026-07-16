package org.westos.service;

import org.westos.entity.Goods;
import com.baomidou.mybatisplus.extension.service.IService;
import org.westos.entity.GoodsREQ;
import org.westos.utils.Result;

import java.util.List;

/**
 * <p>
 * 商品信息表 服务类
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
public interface GoodsService extends IService<Goods> {
    /**
     * 通过供应商id查询商品信息
     *
     * @param supplierId
     * @return
     */
    List<Goods> selectBySupplierId(int supplierId);

    //分页条件查询商品
    Result search(long page, long size, GoodsREQ req);


    //通过id查询商品
    Result findById(int id);

    //更新商品
    Result update(int id, Goods goods);
}
