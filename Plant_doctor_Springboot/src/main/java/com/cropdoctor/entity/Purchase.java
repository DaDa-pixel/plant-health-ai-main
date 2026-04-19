package com.cropdoctor.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

@Data
@TableName("purchase")
public class Purchase {

    @TableId(type = IdType.AUTO)
    private Integer id;

    private String productName;

    private BigDecimal price;

    private Integer quantity;

    private String supplier;

    private String region;

    private String phone;

    private String manager;

    private String remark;

    private Date createTime;

    private Date updateTime;
}