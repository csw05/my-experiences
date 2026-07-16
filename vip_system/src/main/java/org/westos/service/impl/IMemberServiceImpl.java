package org.westos.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.apache.commons.lang.StringUtils;
import org.springframework.stereotype.Service;
import org.westos.entity.Member;
import org.westos.entity.MemberREQ;
import org.westos.mapper.MemberMapper;
import org.westos.service.IMemberService;
import org.westos.utils.Result;

//会员业务接口的实现类
@Service  //注意不要少了@Service 注解
public class IMemberServiceImpl extends ServiceImpl<MemberMapper, Member> implements IMemberService {
    @Override
    public Result search(long page, long size, MemberREQ req) {
        //创建拼接查询条件的类
        QueryWrapper<Member> queryWrapper = new QueryWrapper<>();
        //判断条件有，就拼接上
        if (req != null) {
            //StringUtils是 org.apache.commons.lang下的
            if (StringUtils.isNotBlank(req.getName())) {
                //拼接会员名,注意 "name" 是数据库表中的字段名
                queryWrapper.like("name", req.getName());
            }
            if (StringUtils.isNotBlank(req.getCardNum())) {
                queryWrapper.like("card_num", req.getCardNum());
            }
            if (StringUtils.isNotBlank(req.getPayType())) {
                queryWrapper.eq("pay_type", req.getPayType());
            }
            if (req.getBirthday() != null) {
                queryWrapper.eq("birthday", req.getBirthday());
            }
        }

        //创建分页对象,传入页码和每页条数
        Page<Member> memberPage = new Page<>(page, size);
        //进行分页查询
        Page<Member> memberPageData = baseMapper.selectPage(memberPage, queryWrapper);
        //把分页对象，放进结果集对象中
        return Result.ok(memberPageData);
    }

    //修改会员
    @Override
    public Result update(int id, Member member) {
        if (member.getId() == null) {
            member.setId(id);
        }
        //更新操作
        int size = baseMapper.updateById(member);
        if (size < 1) {
            return Result.error("修改会员信息失败");
        }
        return Result.ok();
    }
}