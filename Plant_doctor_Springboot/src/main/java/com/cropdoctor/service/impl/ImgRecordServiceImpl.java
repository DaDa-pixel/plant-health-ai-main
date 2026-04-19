package com.cropdoctor.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.cropdoctor.entity.ImgRecord;
import com.cropdoctor.mapper.ImgRecordMapper;
import com.cropdoctor.service.ImgRecordService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class ImgRecordServiceImpl extends ServiceImpl<ImgRecordMapper, ImgRecord> implements ImgRecordService {

    @Override
    public Page<ImgRecord> getPage(Integer pageNum, Integer pageSize, String search) {
        Page<ImgRecord> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<ImgRecord> wrapper = new LambdaQueryWrapper<>();

        if (StringUtils.hasText(search)) {
            wrapper.and(w -> w
                .like(ImgRecord::getKind, search)
                .or()
                .like(ImgRecord::getUsername, search)
            );
        }

        wrapper.orderByDesc(ImgRecord::getStartTime);

        return page(page, wrapper);
    }

    @Override
    public boolean deleteById(Integer id) {
        return removeById(id);
    }
}