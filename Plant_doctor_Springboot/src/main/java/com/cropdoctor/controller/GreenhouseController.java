package com.cropdoctor.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.cropdoctor.common.Result;
import com.cropdoctor.entity.Greenhouse;
import com.cropdoctor.service.GreenhouseService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/greenhouse")
public class GreenhouseController {

    @Autowired
    private GreenhouseService greenhouseService;

    @GetMapping
    public Result<Map<String, Object>> getGreenhouseList(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String cropType,
            @RequestParam(required = false) String growthStatus,
            @RequestParam(required = false) String manager) {

        try {
            Page<Greenhouse> page = new Page<>(pageNum, pageSize);
            LambdaQueryWrapper<Greenhouse> wrapper = new LambdaQueryWrapper<>();

            if (search != null && !search.trim().isEmpty()) {
                wrapper.like(Greenhouse::getGreenhouseName, search);
            }
            if (cropType != null && !cropType.trim().isEmpty()) {
                wrapper.like(Greenhouse::getCropType, cropType);
            }
            if (growthStatus != null && !growthStatus.trim().isEmpty()) {
                wrapper.like(Greenhouse::getGrowthStatus, growthStatus);
            }
            if (manager != null && !manager.trim().isEmpty()) {
                wrapper.like(Greenhouse::getManager, manager);
            }

            wrapper.orderByDesc(Greenhouse::getId);
            Page<Greenhouse> resultPage = greenhouseService.page(page, wrapper);

            Map<String, Object> data = new HashMap<>();
            data.put("records", resultPage.getRecords());
            data.put("total", resultPage.getTotal());

            return Result.success(data);
        } catch (Exception e) {
            log.error("获取温室列表异常: {}", e.getMessage());
            return Result.error("获取数据失败: " + e.getMessage());
        }
    }

    @PostMapping
    public Result<String> addGreenhouse(@RequestBody Greenhouse greenhouse) {
        try {
            greenhouse.setCreateTime(new Date());
            greenhouse.setUpdateTime(new Date());
            boolean success = greenhouseService.save(greenhouse);

            if (success) {
                return Result.success("添加成功");
            } else {
                return Result.error("添加失败");
            }
        } catch (Exception e) {
            log.error("添加温室记录异常: {}", e.getMessage());
            return Result.error("添加失败: " + e.getMessage());
        }
    }

    @PutMapping
    public Result<String> updateGreenhouse(@RequestBody Greenhouse greenhouse) {
        try {
            greenhouse.setUpdateTime(new Date());
            boolean success = greenhouseService.updateById(greenhouse);

            if (success) {
                return Result.success("修改成功");
            } else {
                return Result.error("修改失败");
            }
        } catch (Exception e) {
            log.error("修改温室记录异常: {}", e.getMessage());
            return Result.error("修改失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<String> deleteGreenhouse(@PathVariable Integer id) {
        try {
            boolean success = greenhouseService.removeById(id);

            if (success) {
                return Result.success("删除成功");
            } else {
                return Result.error("删除失败");
            }
        } catch (Exception e) {
            log.error("删除温室记录异常: {}", e.getMessage());
            return Result.error("删除失败: " + e.getMessage());
        }
    }
}