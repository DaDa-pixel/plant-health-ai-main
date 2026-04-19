package com.cropdoctor.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.cropdoctor.common.Result;
import com.cropdoctor.entity.Purchase;
import com.cropdoctor.service.PurchaseService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/purchase")
public class PurchaseController {

    @Autowired
    private PurchaseService purchaseService;

    @GetMapping
    public Result<Map<String, Object>> getPurchaseList(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String supplier,
            @RequestParam(required = false) String region,
            @RequestParam(required = false) String manager) {

        try {
            Page<Purchase> page = new Page<>(pageNum, pageSize);
            LambdaQueryWrapper<Purchase> wrapper = new LambdaQueryWrapper<>();

            if (search != null && !search.trim().isEmpty()) {
                wrapper.like(Purchase::getProductName, search);
            }
            if (supplier != null && !supplier.trim().isEmpty()) {
                wrapper.like(Purchase::getSupplier, supplier);
            }
            if (region != null && !region.trim().isEmpty()) {
                wrapper.like(Purchase::getRegion, region);
            }
            if (manager != null && !manager.trim().isEmpty()) {
                wrapper.like(Purchase::getManager, manager);
            }

            wrapper.orderByDesc(Purchase::getId);
            Page<Purchase> resultPage = purchaseService.page(page, wrapper);

            Map<String, Object> data = new HashMap<>();
            data.put("records", resultPage.getRecords());
            data.put("total", resultPage.getTotal());

            return Result.success(data);
        } catch (Exception e) {
            log.error("获取采购列表异常: {}", e.getMessage());
            return Result.error("获取数据失败: " + e.getMessage());
        }
    }

    @PostMapping
    public Result<String> addPurchase(@RequestBody Purchase purchase) {
        try {
            purchase.setCreateTime(new Date());
            purchase.setUpdateTime(new Date());
            boolean success = purchaseService.save(purchase);

            if (success) {
                return Result.success("添加成功");
            } else {
                return Result.error("添加失败");
            }
        } catch (Exception e) {
            log.error("添加采购记录异常: {}", e.getMessage());
            return Result.error("添加失败: " + e.getMessage());
        }
    }

    @PutMapping
    public Result<String> updatePurchase(@RequestBody Purchase purchase) {
        try {
            purchase.setUpdateTime(new Date());
            boolean success = purchaseService.updateById(purchase);

            if (success) {
                return Result.success("修改成功");
            } else {
                return Result.error("修改失败");
            }
        } catch (Exception e) {
            log.error("修改采购记录异常: {}", e.getMessage());
            return Result.error("修改失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<String> deletePurchase(@PathVariable Integer id) {
        try {
            boolean success = purchaseService.removeById(id);

            if (success) {
                return Result.success("删除成功");
            } else {
                return Result.error("删除失败");
            }
        } catch (Exception e) {
            log.error("删除采购记录异常: {}", e.getMessage());
            return Result.error("删除失败: " + e.getMessage());
        }
    }
}