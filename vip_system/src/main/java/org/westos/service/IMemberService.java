package org.westos.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.westos.entity.Member;
import org.westos.entity.MemberREQ;
import org.westos.utils.Result;

//针对会员操作的业务接口
public interface IMemberService extends IService<Member> {
    //分页条件查询的方法

    /**
     * @param page 当前页码
     * @param size 没有调试
     * @param req  封装的查询条件
     * @return
     */
    Result search(long page, long size, MemberREQ req);

    //修改会员的方法
    Result update(int id, Member member);
}