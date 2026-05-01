package com.cropdoctor.controller;

import com.cropdoctor.common.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@Slf4j
@RestController
@RequestMapping("/files")
public class FileUploadController {

    @Value("${file.upload-path}")
    private String uploadPath;

    @PostMapping("/upload")
    public Result<String> upload(@RequestParam("file") MultipartFile file) {
        try {
            if (file.isEmpty()) {
                return Result.error("文件不能为空");
            }

            File dir = new File(uploadPath);
            if (!dir.exists()) {
                dir.mkdirs();
            }

            String originalFilename = file.getOriginalFilename();
            String extension = originalFilename.substring(originalFilename.lastIndexOf("."));
            String fileName = UUID.randomUUID().toString() + extension;

            Path filePath = Paths.get(uploadPath, fileName);
            Files.write(filePath, file.getBytes());

            String fileUrl = "/uploads/" + fileName;
            log.info("文件上传成功: {}", fileUrl);
            return Result.success(fileUrl);

        } catch (IOException e) {
            log.error("文件上传失败: {}", e.getMessage());
            return Result.error("文件上传失败: " + e.getMessage());
        }
    }
}