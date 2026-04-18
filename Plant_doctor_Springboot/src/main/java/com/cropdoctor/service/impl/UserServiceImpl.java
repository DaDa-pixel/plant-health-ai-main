package com.cropdoctor.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.cropdoctor.entity.User;
import com.cropdoctor.mapper.UserMapper;
import com.cropdoctor.service.UserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Slf4j
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    @Override
    public User login(String username, String password) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username)
               .eq(User::getPassword, password);

        User user = this.getOne(wrapper);

        if (user != null) {
            log.info("用户登录成功: {}", username);
            return user;
        } else {
            log.warn("用户登录失败，用户名或密码错误: {}", username);
            return null;
        }
    }

    @Override
    public boolean register(User user) {
        // 检查用户名是否已存在
        User existingUser = findByUsername(user.getUsername());
        if (existingUser != null) {
            log.warn("注册用户失败，用户名已存在: {}", user.getUsername());
            return false;
        }

        // 设置默认值
        if (user.getRole() == null || user.getRole().isEmpty()) {
            user.setRole("common");
        }
        if (user.getAvatar() == null || user.getAvatar().isEmpty()) {
            user.setAvatar("http://localhost:9999/files/15e09359b18544dbb65dc9dadb833abd_人.png");
        }
        user.setTime(LocalDateTime.now());

        boolean result = this.save(user);
        if (result) {
            log.info("用户注册成功: {}", user.getUsername());
        } else {
            log.error("用户注册失败: {}", user.getUsername());
        }

        return result;
    }

    @Override
    public User findByUsername(String username) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username);
        return this.getOne(wrapper);
    }
}