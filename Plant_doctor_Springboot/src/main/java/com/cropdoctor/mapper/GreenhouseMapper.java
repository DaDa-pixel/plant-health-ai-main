package com.cropdoctor.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.cropdoctor.entity.Greenhouse;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface GreenhouseMapper extends BaseMapper<Greenhouse> {
}