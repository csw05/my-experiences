package org.westos.entity;

import java.io.Serializable;

public class GoodsREQ implements Serializable {
    //商品名称
    private String name;
    //商品编码
    private String code;
    //供应商id
    private String supplierId;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getSupplierId() {
        return supplierId;
    }

    public void setSupplierId(String supplierId) {
        this.supplierId = supplierId;
    }

    @Override
    public String toString() {
        return "GoodsREQ{" +
                "name='" + name + '\'' +
                ", code='" + code + '\'' +
                ", supplierId='" + supplierId + '\'' +
                '}';
    }
}