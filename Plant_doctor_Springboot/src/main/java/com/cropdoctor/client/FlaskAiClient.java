package com.cropdoctor.client;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.Map;

@Slf4j
@Component
public class FlaskAiClient {

    @Value("${flask.ai-service.base-url}")
    private String flaskBaseUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    public JSONObject getFileNames() {
        try {
            String url = flaskBaseUrl + "/file_names";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

            if (response.getStatusCode() == HttpStatus.OK) {
                return JSON.parseObject(response.getBody());
            }
        } catch (Exception e) {
            log.error("调用Flask获取模型文件列表失败: {}", e.getMessage());
        }
        return null;
    }

    public String uploadImage(MultipartFile file) {
        try {
            String url = flaskBaseUrl + "/upload";

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new FileSystemResource(convertMultiPartToFile(file)));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);

            if (response.getStatusCode() == HttpStatus.OK) {
                JSONObject result = JSON.parseObject(response.getBody());
                if (result.getInteger("code") == 0) {
                    return result.getString("data");
                }
            }
        } catch (Exception e) {
            log.error("上传图片到Flask服务失败: {}", e.getMessage());
        }
        return null;
    }

    public JSONObject predict(Map<String, Object> params) {
        try {
            String url = flaskBaseUrl + "/predict";

            // 构建multipart请求
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            
            // 添加图片文件
            String inputImg = (String) params.get("inputImg");
            if (inputImg != null && !inputImg.isEmpty()) {
                // 从uploads目录读取文件
                String uploadDir = System.getProperty("user.dir") + "/uploads/";
                File imageFile = new File(uploadDir + inputImg);
                
                if (imageFile.exists()) {
                    body.add("image", new FileSystemResource(imageFile));
                    log.info("准备发送图片到Flask: {}", imageFile.getAbsolutePath());
                } else {
                    log.error("图片文件不存在: {}", imageFile.getAbsolutePath());
                    JSONObject error = new JSONObject();
                    error.put("success", false);
                    error.put("error", "图片文件不存在");
                    return error;
                }
            } else {
                log.error("未提供图片文件名");
                JSONObject error = new JSONObject();
                error.put("success", false);
                error.put("error", "未提供图片");
                return error;
            }

            // 添加参数：是否生成热力图（默认true，启用热力图功能）
            Boolean generateHeatmap = (Boolean) params.getOrDefault("generateHeatmap", true);
            body.add("generate_heatmap", generateHeatmap.toString());
            log.info("热力图生成选项: {}", generateHeatmap);

            // 添加参数：置信度阈值
            Object conf = params.get("conf");
            if (conf != null) {
                body.add("conf", conf.toString());
                log.info("置信度阈值: {}", conf);
            }

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);

            log.info("Flask响应状态: {}", response.getStatusCode());
            log.info("Flask响应内容: {}", response.getBody());

            if (response.getStatusCode() == HttpStatus.OK) {
                return JSON.parseObject(response.getBody());
            }
        } catch (Exception e) {
            log.error("调用Flask预测接口失败: {}", e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    private File convertMultiPartToFile(MultipartFile file) throws Exception {
        File convFile = new File(System.getProperty("java.io.tmpdir") + "/" + file.getOriginalFilename());
        file.transferTo(convFile);
        return convFile;
    }

    public boolean healthCheck() {
        try {
            String url = flaskBaseUrl + "/health";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            log.error("Flask服务健康检查失败: {}", e.getMessage());
            return false;
        }
    }

    public JSONObject searchKnowledge(String keyword) {
        try {
            String url = flaskBaseUrl + "/knowledge/search";
            
            Map<String, String> body = new java.util.HashMap<>();
            body.put("keyword", keyword);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> requestEntity = new HttpEntity<>(body, headers);
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return JSON.parseObject(response.getBody());
            }
        } catch (Exception e) {
            log.error("调用Flask知识库搜索接口失败: {}", e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    public JSONObject getDiseases() {
        try {
            String url = flaskBaseUrl + "/diseases";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return JSON.parseObject(response.getBody());
            }
        } catch (Exception e) {
            log.error("调用Flask获取病害列表接口失败: {}", e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    public JSONObject getEnvAdvice(Map<String, Object> envData) {
        try {
            String url = flaskBaseUrl + "/env_advice";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(envData, headers);
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return JSON.parseObject(response.getBody());
            }
        } catch (Exception e) {
            log.error("调用Flask环境建议接口失败: {}", e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    public JSONObject chat(String message, String diseaseContext) {
        try {
            String url = flaskBaseUrl + "/chat";
            
            Map<String, String> body = new java.util.HashMap<>();
            body.put("message", message);
            if (diseaseContext != null && !diseaseContext.isEmpty()) {
                body.put("disease_context", diseaseContext);
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> requestEntity = new HttpEntity<>(body, headers);
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return JSON.parseObject(response.getBody());
            }
        } catch (Exception e) {
            log.error("调用Flask智能对话接口失败: {}", e.getMessage());
            e.printStackTrace();
        }
        return null;
    }
}