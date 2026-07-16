package org.westos.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;

/**
 * <p>
 * 供应商信息表
 * </p>
 *
 * @author laoshen
 * @since 2025-09-11
 */
@TableName("tb_supplier")
public class Supplier implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    /**
     * 供应商名称
     */
    private String name;

    /**
     * 联系人
     */
    private String linkman;

    /**
     * 联系电话
     */
    private String mobile;

    /**
     * 备注
     */
    private String remark;

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

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    @Override
    public String toString() {
        return "Supplier{" +
        "id = " + id +
        ", name = " + name +
        ", linkman = " + linkman +
        ", mobile = " + mobile +
        ", remark = " + remark +
        "}";
    }
}
