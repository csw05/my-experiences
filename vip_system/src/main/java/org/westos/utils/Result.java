package org.westos.utils;

import com.alibaba.fastjson.JSON;


import java.io.Serializable;


public class Result implements Serializable { //封装响应会前端的数据
    private static final long serialVersionUID = 1L;
    //响应业务状态码 2000 表示成功
    private Integer code;
    //是否成功
    private Boolean flag;
    //响应信息
    private String message;
    //响应中的数据
    private Object data;

    public Result() {
    }

    //有参构造
    public Result(Integer code, String message, Object data, boolean flag) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.flag = flag;
    }

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public Boolean getFlag() {
        return flag;
    }

    public void setFlag(Boolean flag) {
        this.flag = flag;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }

    public static Result ok() {
        return new Result(2000, "成功", null, true);
    }

    public static Result ok(Object data) {
        return new Result(2000, "成功", data, true);
    }

    public static Result ok(String message, Object data) {
        return new Result(2000, message, data, true);
    }

    public static Result error() {
        return new Result(999, "失败", null, false);
    }

    public static Result error(String message) {

        return new Result(999, message, null, false);
    }

    public static Result error(String message, Object data) {
        return new Result(999, message, data, false);
    }

    public static Result build(int code, String message, boolean flag) {
        return new Result(code, message, null, flag);
    }

    public static Result build(int code, String message, Object data, boolean flag) {
        return new Result(code, message, data, flag);
    }


    public String toString() {
        //把响应的Java对象，转换成JSON字符串
        return JSON.toJSONString(this);
    }

}
