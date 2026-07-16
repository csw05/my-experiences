package org.westos.mapper;

import com.baomidou.mybatisplus.core.metadata.IPage;
import org.apache.ibatis.annotations.Param;
import org.westos.entity.Goods;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.westos.entity.GoodsREQ;

/**
 * <p>
 * 商品信息表 Mapper 接口
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
public interface GoodsMapper extends BaseMapper<Goods> {

    /**
     * 不需要手动去分页，mybaits-plus会自动实现分页
     * 但是你必须第1个参数传入IPage对象，
     * 第2个参数查询条件通过 @Param 取别名，
     * 最终查询到的数据会被封装到IPage实现里面
     */
    IPage<Goods> searchPage(IPage<Goods> page, @Param("req") GoodsREQ req);
}
