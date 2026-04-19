package com.cropdoctor.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.cropdoctor.entity.Greenhouse;
import com.cropdoctor.mapper.GreenhouseMapper;
import com.cropdoctor.service.GreenhouseService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class GreenhouseServiceImpl extends ServiceImpl<GreenhouseMapper, Greenhouse> implements GreenhouseService {
}