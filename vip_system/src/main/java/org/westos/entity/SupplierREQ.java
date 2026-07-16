package org.westos.entity;

import java.io.Serializable;

public class SupplierREQ implements Serializable {
    //供应商名称
    private String name;
    //联系人
    private String linkman;
    //联系电话
    private String mobile;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getLinkman() {
        return linkman;
    }

    public void setLinkman(String linkman) {
        this.linkman = linkman;
    }

    public String getMobile() {
        return mobile;
    }

    public void setMobile(String mobile) {
        this.mobile = mobile;
    }

    @Override
    public String toString() {
        return "SupplierREQ{" +
                "name='" + name + '\'' +
                ", linkman='" + linkman + '\'' +
                ", mobile='" + mobile + '\'' +
                '}';
    }
}