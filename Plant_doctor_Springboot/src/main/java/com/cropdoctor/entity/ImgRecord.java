package com.cropdoctor.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("imgrecords")
public class ImgRecord {

    @TableId(type = IdType.AUTO)
    private Integer id;

    @TableField("input_img")
    private String inputImg;

    @TableField("out_img")
    private String outImg;

    private String confidence;

    @TableField("all_time")
    private String allTime;

    private String conf;

    private String weight;

    private String username;

    @TableField("start_time")
    private String startTime;

    private String label;

    private String kind;
}