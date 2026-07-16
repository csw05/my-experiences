package org.westos.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.westos.entity.Member;
import org.westos.entity.MemberREQ;
import org.westos.service.IMemberService;
import org.westos.utils.Result;

@RestController
@RequestMapping(path = "/member")
public class MemberController {
    //注入
    @Autowired // 不要少了注解
    private IMemberService memberService;
    //分页查询

    /**
     * 分页条件查询会员列表
     *
     * @param page 页码
     * @param size 每页显示记录数
     * @param req  查询条件
     * @return
     */
    @PostMapping("/list/search/{page}/{size}")
    public Result search(@PathVariable("page") long page,
                         @PathVariable("size") long size,
                         @RequestBody(required = false) MemberREQ req) {
        //System.out.println(page);
        //System.out.println(size);
        return memberService.search(page, size, req);
    }

    //新增会员
    @PostMapping // /member
    // @RequestBody 表示获取请求体中的数据，因为前台发送post请求，在请求体中放的是JSON数据，所以通过 @RequestBody来获取
    public Result add(@RequestBody Member member) {
        boolean b = memberService.save(member);
        if (b) {
            return Result.ok();
        }
        return Result.error("新增会员信息失败");
    }

    //根据id删除
    @DeleteMapping("/{id}")
    public Result delete(@PathVariable("id") int id) {
        boolean b = memberService.removeById(id);
        if (b) {
            return Result.ok();
        }
        return Result.error("删除会员信息失败");
    }

    @GetMapping("/{id}") // /member/{id}
    public Result get(@PathVariable("id") int id) {
        //getById(id) 这个方法IService即可中实现了，所以直接调用即可
        Member member = memberService.getById(id);
        return Result.ok(member);
    }

    //修改的方法
    @PutMapping("/{id}") // /member/{id}
    public Result update(@PathVariable("id") int id,
                         @RequestBody Member member) {
        //update()这个方法需要我们在IMemberService接口定义
        return memberService.update(id, member);
    }
}
