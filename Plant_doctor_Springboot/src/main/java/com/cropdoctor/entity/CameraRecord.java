package com.cropdoctor.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("camerarecords")
public class CameraRecord {

    @TableId(type = IdType.AUTO)
    private Integer id;

    private String weight;

    private String conf;

    private String username;

    @TableField("start_time")
    private String startTime;

    @TableField("out_video")
    private String outVideo;

    private String kind;
}