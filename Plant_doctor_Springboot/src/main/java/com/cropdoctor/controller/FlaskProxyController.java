package com.cropdoctor.controller;

import com.alibaba.fastjson.JSONObject;
import com.cropdoctor.client.FlaskAiClient;
import com.cropdoctor.common.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/flask")
public class FlaskProxyController {

    @Autowired
    private FlaskAiClient flaskAiClient;

    @GetMapping("/file_names")
    public Result<String> getFileNames() {
        try {
            JSONObject result = flaskAiClient.getFileNames();
            if (result != null) {
                return Result.success(result.getString("data"));
            }
            return Result.error("获取模型文件列表失败");
        } catch (Exception e) {
            log.error("获取模型文件列表异常: {}", e.getMessage());
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/upload")
    public Result<String> uploadFile(@RequestParam("file") MultipartFile file) {
        try {
            if (file.isEmpty()) {
                return Result.error("文件不能为空");
            }

            String fileUrl = flaskAiClient.uploadImage(file);
            if (fileUrl != null) {
                String fileName = fileUrl.substring(fileUrl.lastIndexOf("/") + 1);
                return Result.success(fileName);
            }
            return Result.error("文件上传失败");
        } catch (Exception e) {
            log.error("文件上传异常: {}", e.getMessage());
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/predict")
    public Result<String> predict(@RequestBody Map<String, Object> params) {
        try {
            log.info("收到预测请求: {}", params);

            JSONObject result = flaskAiClient.predict(params);
            if (result != null && result.getBooleanValue("success")) {
                return Result.success(result.toJSONString());
            }

            String errorMsg = result != null ? result.getString("error") : "预测失败";
            return Result.error(errorMsg);
        } catch (Exception e) {
            log.error("预测异常: {}", e.getMessage());
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/health")
    public Result<Boolean> health() {
        boolean isHealthy = flaskAiClient.healthCheck();
        return Result.success(isHealthy);
    }

    @PostMapping("/knowledge/search")
    public Result<Object> searchKnowledge(@RequestBody Map<String, String> params) {
        try {
            log.info("收到知识库搜索请求: {}", params);
            
            JSONObject result = flaskAiClient.searchKnowledge(params.get("keyword"));
            if (result != null && result.getBooleanValue("success")) {
                return Result.success(result);
            }
            
            String errorMsg = result != null ? result.getString("error") : "搜索失败";
            return Result.error(errorMsg);
        } catch (Exception e) {
            log.error("知识库搜索异常: {}", e.getMessage());
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/diseases")
    public Result<Object> getDiseases() {
        try {
            log.info("收到获取病害列表请求");
            
            JSONObject result = flaskAiClient.getDiseases();
            if (result != null && result.getBooleanValue("success")) {
                return Result.success(result);
            }
            
            return Result.error("获取病害列表失败");
        } catch (Exception e) {
            log.error("获取病害列表异常: {}", e.getMessage());
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/env_advice")
    public Result<Object> getEnvAdvice(@RequestBody Map<String, Object> envData) {
        try {
            log.info("收到环境监测建议请求: {}", envData);
            
            JSONObject result = flaskAiClient.getEnvAdvice(envData);
            if (result != null && result.getBooleanValue("success")) {
                return Result.success(result);
            }
            
            String errorMsg = result != null ? result.getString("error") : "获取环境建议失败";
            return Result.error(errorMsg);
        } catch (Exception e) {
            log.error("获取环境建议异常: {}", e.getMessage());
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/chat")
    public Result<Object> chat(@RequestBody Map<String, String> params) {
        try {
            log.info("收到智能对话请求: {}", params);
            
            JSONObject result = flaskAiClient.chat(params.get("message"), params.get("disease_context"));
            if (result != null && result.getBooleanValue("success")) {
                return Result.success(result);
            }
            
            String errorMsg = result != null ? result.getString("error") : "对话失败";
            return Result.error(errorMsg);
        } catch (Exception e) {
            log.error("智能对话异常: {}", e.getMessage());
            return Result.error(e.getMessage());
        }
    }
}