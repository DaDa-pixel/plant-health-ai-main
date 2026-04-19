package com.cropdoctor.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.cropdoctor.entity.CameraRecord;

public interface CameraRecordService extends IService<CameraRecord> {

    Page<CameraRecord> getPage(Integer pageNum, Integer pageSize, String search);

    boolean deleteById(Integer id);
}