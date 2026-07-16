package org.westos.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.apache.commons.lang.StringUtils;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.westos.entity.PasswordREQ;
import org.westos.entity.Staff;
import org.westos.entity.StaffREQ;
import org.westos.mapper.StaffMapper;
import org.westos.service.StaffService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import org.westos.utils.Result;

/**
 * <p>
 * 员工信息表 服务实现类
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@Service
public class StaffServiceImpl extends ServiceImpl<StaffMapper, Staff> implements StaffService {
    @Override
    public Result search(long page, long size, StaffREQ req) {
        // 封装查询条件
        QueryWrapper<Staff> query = new QueryWrapper<>();
        if (req != null) {
            if (StringUtils.isNotBlank(req.getName())) {
                query.like("name", req.getName());
            }
            if (StringUtils.isNotBlank(req.getUsername())) {
                query.like("username", req.getUsername());
            }
        }

        IPage<Staff> data = baseMapper.selectPage(new Page<Staff>(page, size), query);

        return Result.ok(data);
    }

    @Override
    public Result add(Staff staff) {
        if (staff == null || StringUtils.isEmpty(staff.getUsername())) {
            return Result.error("用户名不能为空");
        }

        // 1. 查询用户名是否存在，抽取一个方法
        Staff s = getByUsername(staff.getUsername());
        if (s != null) {
            return Result.error("用户名已存在");
        }

        // 2. 使用SpringSecurity提供的加密器加密
        String password = new BCryptPasswordEncoder().encode(staff.getPassword());
        staff.setPassword(password);

        // 3. 保存到数据库 这个save()方法是 IService 接口中提供的，直接调用即可
        boolean b = this.save(staff);
        if (b) {
            return Result.ok();
        }
        return Result.error("新增失败");
    }

    //根据用户名查询该用户
    private Staff getByUsername(String username) {
        QueryWrapper<Staff> query = new QueryWrapper<>();
        query.eq("username", username);
        return baseMapper.selectOne(query);
    }

    @Override
    public Result update(int id, Staff staff) {
        if (staff.getId() == null) {
            staff.setId(id);
        }
        //更新操作
        int size = baseMapper.updateById(staff);
        if (size < 1) {
            return Result.error("修改员工信息失败");
        }
        return Result.ok();
    }


    //校验旧密码
    @Override
    public Result checkPassword(PasswordREQ req) {
        if (req == null || StringUtils.isEmpty(req.getPassword())) {
            return Result.error("原密码不能为空");
        }
        //通过员工id查询员工详情
        Staff staff = baseMapper.selectById(req.getUserId());
        //比对前台输入的明文旧密码和数据库中的加密之后的密码进行比对
        if (!new BCryptPasswordEncoder().matches(req.getPassword(), staff.getPassword())) {
            return Result.error("原密码错误");
        }
        return Result.ok();
    }

    //修改密码
    @Override
    public Result updatePassword(PasswordREQ req) {
        if (req == null || StringUtils.isEmpty(req.getPassword())) {
            return Result.error("新密码不能为空");
        }
        // 更新密码
        Staff staff = baseMapper.selectById(req.getUserId());
        staff.setPassword(new BCryptPasswordEncoder().encode(req.getPassword()));
        baseMapper.updateById(staff);
        return Result.ok();
    }
}
