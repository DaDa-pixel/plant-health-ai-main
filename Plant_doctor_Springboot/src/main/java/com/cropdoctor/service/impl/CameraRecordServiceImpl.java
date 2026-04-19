package com.cropdoctor.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.cropdoctor.entity.CameraRecord;
import com.cropdoctor.mapper.CameraRecordMapper;
import com.cropdoctor.service.CameraRecordService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class CameraRecordServiceImpl extends ServiceImpl<CameraRecordMapper, CameraRecord> implements CameraRecordService {

    @Override
    public Page<CameraRecord> getPage(Integer pageNum, Integer pageSize, String search) {
        Page<CameraRecord> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<CameraRecord> wrapper = new LambdaQueryWrapper<>();

        if (StringUtils.hasText(search)) {
            wrapper.and(w -> w
                .like(CameraRecord::getKind, search)
                .or()
                .like(CameraRecord::getUsername, search)
            );
        }

        wrapper.orderByDesc(CameraRecord::getStartTime);

        return page(page, wrapper);
    }

    @Override
    public boolean deleteById(Integer id) {
        return removeById(id);
    }
}