package org.westos.service;

import org.westos.entity.Supplier;
import com.baomidou.mybatisplus.extension.service.IService;
import org.westos.entity.SupplierREQ;
import org.westos.utils.Result;

/**
 * <p>
 * 供应商信息表 服务类
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
public interface SupplierService extends IService<Supplier> {
    //分页带有条件的查询供应商
    Result search(long page, long size, SupplierREQ req);

    //根据id删除供应商
    Result deleteById(int id);

    //根据id修改的方法
    Result update(int id, Supplier supplier);
}
