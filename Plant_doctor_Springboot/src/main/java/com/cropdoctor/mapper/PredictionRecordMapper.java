package com.cropdoctor.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.cropdoctor.entity.PredictionRecord;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PredictionRecordMapper extends BaseMapper<PredictionRecord> {
}