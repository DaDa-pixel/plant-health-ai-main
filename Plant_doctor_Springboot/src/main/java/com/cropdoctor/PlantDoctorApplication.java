package com.cropdoctor;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.cropdoctor.mapper")
public class PlantDoctorApplication {
    public static void main(String[] args) {
        SpringApplication.run(PlantDoctorApplication.class, args);
        System.out.println("========================================");
        System.out.println("🌱 植物医生系统启动成功！");
        System.out.println("========================================");
    }
}