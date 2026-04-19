package com.cropdoctor.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

@Data
@TableName("greenhouse")
public class Greenhouse {

    @TableId(type = IdType.AUTO)
    private Integer id;

    private String greenhouseName;

    private String cropType;

    private Integer quantity;

    private String growthStatus;

    private BigDecimal temperature;

    private Integer airHumidity;

    private Integer soilHumidity;

    private Integer co2Concentration;

    private BigDecimal soilPh;

    private Integer lightIntensity;

    private String manager;

    private String recordTime;

    private Date createTime;

    private Date updateTime;
}