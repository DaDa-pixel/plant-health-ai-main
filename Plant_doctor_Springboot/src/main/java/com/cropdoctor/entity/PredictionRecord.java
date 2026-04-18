package com.cropdoctor.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName("prediction_record")
public class PredictionRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String username;

    private String inputImg;

    private String outputImg;

    private String diseaseName;

    private String confidence;

    private String kind;

    private String weight;

    private Date startTime;

    private Date createTime;
}