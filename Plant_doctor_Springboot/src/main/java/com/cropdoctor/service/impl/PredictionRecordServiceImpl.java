package com.cropdoctor.service.impl;

import com.baomidou.mybatisplus.extension.service.IService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.cropdoctor.entity.PredictionRecord;
import com.cropdoctor.mapper.PredictionRecordMapper;
import org.springframework.stereotype.Service;

@Service
public class PredictionRecordServiceImpl extends ServiceImpl<PredictionRecordMapper, PredictionRecord>
        implements IService<PredictionRecord> {
}