package com.cropdoctor.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.cropdoctor.entity.ImgRecord;

public interface ImgRecordService extends IService<ImgRecord> {

    Page<ImgRecord> getPage(Integer pageNum, Integer pageSize, String search);

    boolean deleteById(Integer id);
}