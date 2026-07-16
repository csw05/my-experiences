package org.westos.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * <p>
 * 商品信息表
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@TableName("tb_goods")
public class Goods implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    /**
     * 商品名称
     */
    private String name;

    /**
     * 商品编码
     */
    private String code;

    /**
     * 商品规格
     */
    private String spec;

    /**
     * 零售价
     */
    private BigDecimal retailPrice;

    /**
     * 进货价
     */
    private BigDecimal purchasePrice;

    /**
     * 库存数量
     */
    private Integer storageNum;

    /**
     * 供应商id
     */
    private Integer supplierId;

    // 供应商名称
    // 注意:标识它不是tb_goods表中字段，不然会报错
    @TableField(exist = false)
    private String supplierName;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

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

    public String getSpec() {
        return spec;
    }

    public void setSpec(String spec) {
        this.spec = spec;
    }

    public BigDecimal getRetailPrice() {
        return retailPrice;
    }

    public void setRetailPrice(BigDecimal retailPrice) {
        this.retailPrice = retailPrice;
    }

    public BigDecimal getPurchasePrice() {
        return purchasePrice;
    }

    public void setPurchasePrice(BigDecimal purchasePrice) {
        this.purchasePrice = purchasePrice;
    }

    public Integer getStorageNum() {
        return storageNum;
    }

    public void setStorageNum(Integer storageNum) {
        this.storageNum = storageNum;
    }

    public Integer getSupplierId() {
        return supplierId;
    }

    public void setSupplierId(Integer supplierId) {
        this.supplierId = supplierId;
    }

    public String getSupplierName() {
        return supplierName;
    }

    public void setSupplierName(String supplierName) {
        this.supplierName = supplierName;
    }

    @Override
    public String toString() {
        return "Goods{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", code='" + code + '\'' +
                ", spec='" + spec + '\'' +
                ", retailPrice=" + retailPrice +
                ", purchasePrice=" + purchasePrice +
                ", storageNum=" + storageNum +
                ", supplierId=" + supplierId +
                ", supplierName='" + supplierName + '\'' +
                '}';
    }
}
