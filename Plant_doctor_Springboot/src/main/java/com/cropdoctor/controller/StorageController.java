package com.cropdoctor.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.cropdoctor.common.Result;
import com.cropdoctor.entity.Storage;
import com.cropdoctor.service.StorageService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/storage")
public class StorageController {

    @Autowired
    private StorageService storageService;

    @GetMapping
    public Result<Map<String, Object>> getStorageList(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String warehouse,
            @RequestParam(required = false) String storageArea,
            @RequestParam(required = false) String manager) {

        try {
            Page<Storage> page = new Page<>(pageNum, pageSize);
            LambdaQueryWrapper<Storage> wrapper = new LambdaQueryWrapper<>();

            if (search != null && !search.trim().isEmpty()) {
                wrapper.like(Storage::getProduct, search);
            }
            if (warehouse != null && !warehouse.trim().isEmpty()) {
                wrapper.like(Storage::getWarehouse, warehouse);
            }
            if (storageArea != null && !storageArea.trim().isEmpty()) {
                wrapper.like(Storage::getStorageArea, storageArea);
            }
            if (manager != null && !manager.trim().isEmpty()) {
                wrapper.like(Storage::getManager, manager);
            }

            wrapper.orderByDesc(Storage::getId);
            Page<Storage> resultPage = storageService.page(page, wrapper);

            Map<String, Object> data = new HashMap<>();
            data.put("records", resultPage.getRecords());
            data.put("total", resultPage.getTotal());

            return Result.success(data);
        } catch (Exception e) {
            log.error("获取库存列表异常: {}", e.getMessage());
            return Result.error("获取数据失败: " + e.getMessage());
        }
    }

    @PostMapping
    public Result<String> addStorage(@RequestBody Storage storage) {
        try {
            storage.setCreateTime(new Date());
            storage.setUpdateTime(new Date());
            boolean success = storageService.save(storage);

            if (success) {
                return Result.success("添加成功");
            } else {
                return Result.error("添加失败");
            }
        } catch (Exception e) {
            log.error("添加库存记录异常: {}", e.getMessage());
            return Result.error("添加失败: " + e.getMessage());
        }
    }

    @PutMapping
    public Result<String> updateStorage(@RequestBody Storage storage) {
        try {
            storage.setUpdateTime(new Date());
            boolean success = storageService.updateById(storage);

            if (success) {
                return Result.success("修改成功");
            } else {
                return Result.error("修改失败");
            }
        } catch (Exception e) {
            log.error("修改库存记录异常: {}", e.getMessage());
            return Result.error("修改失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<String> deleteStorage(@PathVariable Integer id) {
        try {
            boolean success = storageService.removeById(id);

            if (success) {
                return Result.success("删除成功");
            } else {
                return Result.error("删除失败");
            }
        } catch (Exception e) {
            log.error("删除库存记录异常: {}", e.getMessage());
            return Result.error("删除失败: " + e.getMessage());
        }
    }
}