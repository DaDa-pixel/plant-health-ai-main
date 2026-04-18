package com.cropdoctor.controller;

import com.cropdoctor.common.Result;
import com.cropdoctor.entity.User;
import com.cropdoctor.service.UserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

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
                data.put("avatar", user.getAvatar());

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
                data.put("avatar", user.getAvatar());

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
}
