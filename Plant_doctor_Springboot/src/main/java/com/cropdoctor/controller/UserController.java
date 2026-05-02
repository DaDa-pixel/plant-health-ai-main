package com.cropdoctor.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.cropdoctor.common.Result;
import com.cropdoctor.entity.User;
import com.cropdoctor.service.UserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * 兼容旧数据：如果头像路径不以 / 或 http 开头，补上 /uploads/ 前缀
     */
    private String normalizeAvatar(String avatar) {
        if (avatar == null || avatar.isEmpty()) {
            return avatar;
        }
        // 将硬编码的 localhost URL 转为相对路径，便于反向代理访问
        if (avatar.startsWith("http://localhost:9999/")) {
            return avatar.substring(avatar.indexOf("/files"));
        }
        if (avatar.startsWith("/") || avatar.startsWith("http")) {
            return avatar;
        }
        return "/uploads/" + avatar;
    }

    /**
     * 用户登录
     */
    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody Map<String, String> params) {
        try {
            String username = params.get("username");
            String password = params.get("password");

            if (username == null || username.trim().isEmpty()) {
                return Result.error("用户名不能为空");
            }
            if (password == null || password.trim().isEmpty()) {
                return Result.error("密码不能为空");
            }

            User user = userService.login(username, password);

            if (user != null) {
                Map<String, Object> data = new HashMap<>();
                data.put("id", user.getId());
                data.put("username", user.getUsername());
                data.put("name", user.getName());
                data.put("sex", user.getSex());
                data.put("email", user.getEmail());
                data.put("tel", user.getTel());
                data.put("role", user.getRole());
                data.put("avatar", normalizeAvatar(user.getAvatar()));

                log.info("用户登录成功: {}", username);
                return Result.success(data);
            } else {
                return Result.error("用户名或密码错误");
            }
        } catch (Exception e) {
            log.error("登录异常: {}", e.getMessage());
            return Result.error("登录失败: " + e.getMessage());
        }
    }

    /**
     * 用户注册
     */
    @PostMapping("/register")
    public Result<String> register(@RequestBody User user) {
        try {
            if (user.getUsername() == null || user.getUsername().trim().isEmpty()) {
                return Result.error("用户名不能为空");
            }
            if (user.getPassword() == null || user.getPassword().trim().isEmpty()) {
                return Result.error("密码不能为空");
            }

            boolean success = userService.register(user);

            if (success) {
                return Result.success("注册成功");
            } else {
                return Result.error("用户名已存在");
            }
        } catch (Exception e) {
            log.error("注册异常: {}", e.getMessage());
            return Result.error("注册失败: " + e.getMessage());
        }
    }

    /**
     * 获取用户信息
     */
    @GetMapping("/{username}")
    public Result<Map<String, Object>> getUserInfo(@PathVariable String username) {
        try {
            User user = userService.findByUsername(username);

            if (user != null) {
                Map<String, Object> data = new HashMap<>();
                data.put("id", user.getId());
                data.put("username", user.getUsername());
                data.put("name", user.getName());
                data.put("sex", user.getSex());
                data.put("email", user.getEmail());
                data.put("tel", user.getTel());
                data.put("role", user.getRole());
                data.put("avatar", normalizeAvatar(user.getAvatar()));

                return Result.success(data);
            } else {
                return Result.error("用户不存在");
            }
        } catch (Exception e) {
            log.error("获取用户信息异常: {}", e.getMessage());
            return Result.error("获取用户信息失败: " + e.getMessage());
        }
    }

    /**
     * 更新用户信息
     */
    @PostMapping("/update")
    public Result<String> updateUser(@RequestBody User user) {
        try {
            if (user.getId() == null) {
                return Result.error("用户ID不能为空");
            }

            // 保留原有密码，防止前端未传密码或传了掩码密码时被清空
            if (user.getPassword() == null || user.getPassword().isEmpty() || "******".equals(user.getPassword())) {
                User existing = userService.getById(user.getId());
                if (existing != null) {
                    user.setPassword(existing.getPassword());
                }
            }

            boolean success = userService.updateById(user);

            if (success) {
                return Result.success("更新成功");
            } else {
                return Result.error("更新失败");
            }
        } catch (Exception e) {
            log.error("更新用户信息异常: {}", e.getMessage());
            return Result.error("更新失败: " + e.getMessage());
        }
    }

    /**
     * 分页查询用户列表
     * 供用户管理页面使用
     */
    @GetMapping
    public Result<Map<String, Object>> listUsers(
            @RequestParam(required = false, defaultValue = "") String search,
            @RequestParam(required = false, defaultValue = "1") Integer pageNum,
            @RequestParam(required = false, defaultValue = "10") Integer pageSize) {
        try {
            LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
            if (search != null && !search.isEmpty()) {
                wrapper.like(User::getUsername, search)
                       .or()
                       .like(User::getName, search)
                       .or()
                       .like(User::getTel, search);
            }
            wrapper.orderByDesc(User::getId);

            Page<User> page = new Page<>(pageNum, pageSize);
            Page<User> result = userService.page(page, wrapper);

            // 处理头像路径
            for (User user : result.getRecords()) {
                user.setAvatar(normalizeAvatar(user.getAvatar()));
                // 脱敏密码，前端不需要展示真实密码
                user.setPassword("******");
            }

            Map<String, Object> data = new HashMap<>();
            data.put("records", result.getRecords());
            data.put("total", result.getTotal());
            data.put("pageNum", result.getCurrent());
            data.put("pageSize", result.getSize());

            // 统计所有用户中管理员和普通用户的总数（不受搜索/分页影响）
            LambdaQueryWrapper<User> adminWrapper = new LambdaQueryWrapper<>();
            adminWrapper.eq(User::getRole, "admin");
            data.put("adminCount", userService.count(adminWrapper));

            LambdaQueryWrapper<User> commonWrapper = new LambdaQueryWrapper<>();
            commonWrapper.eq(User::getRole, "common");
            data.put("commonCount", userService.count(commonWrapper));

            return Result.success(data);
        } catch (Exception e) {
            log.error("查询用户列表异常: {}", e.getMessage());
            return Result.error("查询用户列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取用户详情（含真实密码），供编辑对话框使用
     */
    @GetMapping("/detail/{id}")
    public Result<Map<String, Object>> getUserDetail(@PathVariable Integer id) {
        try {
            User user = userService.getById(id);
            if (user != null) {
                Map<String, Object> data = new HashMap<>();
                data.put("id", user.getId());
                data.put("username", user.getUsername());
                data.put("password", user.getPassword());
                data.put("name", user.getName());
                data.put("sex", user.getSex());
                data.put("email", user.getEmail());
                data.put("tel", user.getTel());
                data.put("role", user.getRole());
                data.put("avatar", normalizeAvatar(user.getAvatar()));
                return Result.success(data);
            } else {
                return Result.error("用户不存在");
            }
        } catch (Exception e) {
            log.error("获取用户详情异常: {}", e.getMessage());
            return Result.error("获取用户详情失败: " + e.getMessage());
        }
    }

    /**
     * 删除用户
     */
    @DeleteMapping("/{id}")
    public Result<String> deleteUser(@PathVariable Integer id) {
        try {
            boolean success = userService.removeById(id);
            if (success) {
                log.info("删除用户成功: id={}", id);
                return Result.success("删除成功");
            } else {
                return Result.error("用户不存在");
            }
        } catch (Exception e) {
            log.error("删除用户异常: {}", e.getMessage());
            return Result.error("删除失败: " + e.getMessage());
        }
    }

    /**
     * 新增用户（管理员创建用户）
     */
    @PostMapping
    public Result<String> createUser(@RequestBody User user) {
        try {
            if (user.getUsername() == null || user.getUsername().trim().isEmpty()) {
                return Result.error("用户名不能为空");
            }
            if (user.getPassword() == null || user.getPassword().trim().isEmpty()) {
                return Result.error("密码不能为空");
            }

            // 检查用户名是否已存在
            User existing = userService.findByUsername(user.getUsername());
            if (existing != null) {
                return Result.error("用户名已存在");
            }

            // 设置默认值
            if (user.getRole() == null || user.getRole().isEmpty()) {
                user.setRole("common");
            }
            if (user.getAvatar() == null || user.getAvatar().isEmpty()) {
                user.setAvatar("/files/15e09359b18544dbb65dc9dadb833abd_人.png");
            }
            user.setTime(LocalDateTime.now());

            boolean success = userService.save(user);
            if (success) {
                log.info("管理员创建用户成功: {}", user.getUsername());
                return Result.success("创建成功");
            } else {
                return Result.error("创建失败");
            }
        } catch (Exception e) {
            log.error("创建用户异常: {}", e.getMessage());
            return Result.error("创建失败: " + e.getMessage());
        }
    }
}
