package org.westos.entity;

import java.io.Serializable;
import java.util.Date;

//会员查询条件请求类
public class MemberREQ implements Serializable {
    //会员姓名
    private String name;
    //卡号
    private String cardNum;
    //支付类型（'1'现金, '2'微信, '3'支付宝, '4'银行卡）
    private String payType;
    //会员生日
    private Date birthday;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCardNum() {
        return cardNum;
    }

    public void setCardNum(String cardNum) {
        this.cardNum = cardNum;
    }

    public String getPayType() {
        return payType;
    }

    public void setPayType(String payType) {
        this.payType = payType;
    }

    public Date getBirthday() {
        return birthday;
    }

    public void setBirthday(Date birthday) {
        this.birthday = birthday;
    }

    @Override
    public String toString() {
        return "MemberREQ{" +
                "name='" + name + '\'' +
                ", cardNum='" + cardNum + '\'' +
                ", payType='" + payType + '\'' +
                ", birthday=" + birthday +
                '}';
    }
}
