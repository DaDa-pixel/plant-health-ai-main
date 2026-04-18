package com.cropdoctor.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.cropdoctor.entity.User;

public interface UserService extends IService<User> {

    /**
     * 用户登录
     */
    User login(String username, String password);

    /**
     * 用户注册
     */
    boolean register(User user);

    /**
     * 根据用户名查询用户
     */
    User findByUsername(String username);
}