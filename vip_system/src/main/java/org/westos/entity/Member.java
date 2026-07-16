package org.westos.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.io.Serializable;
import java.util.Date;

@TableName("tb_member") //实体类对应的表
public class Member implements Serializable {
    //主键id
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;
    //会员卡号
    private String cardNum;
    //会员名字
    private String name;
    //生日
    private Date birthday;
    //手机号
    private String phone;
    //可用积分
    private Integer integral;
    //可用金额
    private Double money;
    //支付类型（'1'现金, '2'微信, '3'支付宝, '4'银行卡）
    private String payType;
    //会员地址
    private String address;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getCardNum() {
        return cardNum;
    }

    public void setCardNum(String cardNum) {
        this.cardNum = cardNum;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Date getBirthday() {
        return birthday;
    }

    public void setBirthday(Date birthday) {
        this.birthday = birthday;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public Integer getIntegral() {
        return integral;
    }

    public void setIntegral(Integer integral) {
        this.integral = integral;
    }

    public Double getMoney() {
        return money;
    }

    public void setMoney(Double money) {
        this.money = money;
    }

    public String getPayType() {
        return payType;
    }

    public void setPayType(String payType) {
        this.payType = payType;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    @Override
    public String toString() {
        return "Member{" +
                "id=" + id +
                ", cardNum='" + cardNum + '\'' +
                ", name='" + name + '\'' +
                ", birthday=" + birthday +
                ", phone='" + phone + '\'' +
                ", integral=" + integral +
                ", money=" + money +
                ", payType='" + payType + '\'' +
                ", address='" + address + '\'' +
                '}';
    }
}
