package com.cropdoctor.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.cropdoctor.common.Result;
import com.cropdoctor.entity.ImgRecord;
import com.cropdoctor.service.ImgRecordService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/imgRecords")
public class ImgRecordController {

    @Resource
    private ImgRecordService imgRecordService;

    @PostMapping
    public Result<String> saveRecord(@RequestBody Map<String, Object> params) {
        try {
            ImgRecord record = new ImgRecord();
            record.setInputImg((String) params.get("inputImg"));
            record.setOutImg((String) params.get("outImg"));
            record.setConfidence((String) params.get("confidence"));
            record.setAllTime((String) params.get("allTime"));
            record.setConf((String) params.get("conf"));
            record.setWeight((String) params.get("weight"));
            record.setUsername((String) params.get("username"));
            record.setStartTime((String) params.get("startTime"));
            record.setLabel((String) params.get("label"));
            record.setKind((String) params.get("kind"));

            boolean success = imgRecordService.save(record);
            if (success) {
                return Result.success("保存成功");
            } else {
                return Result.error("保存失败");
            }
        } catch (Exception e) {
            log.error("保存图片识别记录失败: {}", e.getMessage());
            return Result.error("保存失败: " + e.getMessage());
        }
    }

    @GetMapping
    public Result<Map<String, Object>> getPage(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String search1) {

        try {
            log.info("获取图片记录 - pageNum: {}, pageSize: {}, search: {}, search1: {}", 
                     pageNum, pageSize, search, search1);
            
            String finalSearch = search != null ? search : search1;
            Page<ImgRecord> page = imgRecordService.getPage(pageNum, pageSize, finalSearch);

            log.info("分页查询结果 - total: {}, current: {}, size: {}, records size: {}", 
                     page.getTotal(), page.getCurrent(), page.getSize(), page.getRecords().size());

            Map<String, Object> data = new HashMap<>();
            data.put("records", page.getRecords());
            data.put("total", page.getTotal());
            data.put("pageNum", page.getCurrent());
            data.put("pageSize", page.getSize());

            log.info("返回数据 - total: {}, records size: {}", page.getTotal(), page.getRecords().size());
            return Result.success(data);
        } catch (Exception e) {
            log.error("获取图片识别记录失败: {}", e.getMessage(), e);
            return Result.error("获取记录失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<String> deleteById(@PathVariable Integer id) {
        try {
            boolean success = imgRecordService.deleteById(id);
            if (success) {
                return Result.success("删除成功");
            } else {
                return Result.error("删除失败");
            }
        } catch (Exception e) {
            log.error("删除图片识别记录失败: {}", e.getMessage());
            return Result.error("删除失败: " + e.getMessage());
        }
    }
}