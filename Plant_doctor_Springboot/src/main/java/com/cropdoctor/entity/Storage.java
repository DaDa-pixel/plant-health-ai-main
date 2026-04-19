package com.cropdoctor.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName("storage")
public class Storage {

    @TableId(type = IdType.AUTO)
    private Integer id;

    private String product;

    private String warehouse;

    private String storageArea;

    private Integer quantity;

    private String manager;

    private String phone;

    private String remark;

    private Date createTime;

    private Date updateTime;
}