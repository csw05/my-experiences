package org.westos.service;

import org.westos.entity.PasswordREQ;
import org.westos.entity.Staff;
import com.baomidou.mybatisplus.extension.service.IService;
import org.westos.entity.StaffREQ;
import org.westos.utils.Result;

/**
 * <p>
 * 员工信息表 服务类
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
public interface StaffService extends IService<Staff> {
    //分页条件查询的方法
    Result search(long page, long size, StaffREQ req);

    //新增员工的方法
    Result add(Staff staff);

    //修改员工的方法
    Result update(int id, Staff staff);

    //校验原密码是否正确
    Result checkPassword(PasswordREQ req);

    //更新修改后的新密码
    Result updatePassword(PasswordREQ req);
}
