<template>
	<div class="system-predict-container layout-padding">
		<div class="system-predict-padding layout-padding-auto layout-padding-view">
			<div class="header">
				<div class="conf" style="display: flex; flex-direction: row; align-items: center;">
					<div style="font-size: 14px;margin-right: 20px;color: #909399;">
						设置最小置信度阈值
					</div>
					<el-slider v-model="conf" :format-tooltip="formatTooltip" style="width: 300px;" />
				</div>
				<div class="button-section" style="margin-left: auto">
					<el-button type="primary" @click="upData" class="predict-button" :loading="state.predictLoading">
						开始预测
					</el-button>
				</div>
			</div>

			<!-- 图片显示区域 -->
			<el-row :gutter="20" class="image-display">
				<!-- 原图展示 -->
				<el-col :span="8">
					<el-card shadow="hover" class="card">
						<div class="image-title">原图片</div>
						<el-upload
							v-model="state.img"
							ref="uploadFile"
							class="avatar-uploader"
							action="/api/files/upload"
							:show-file-list="false"
							:on-success="handleAvatarSuccessone"
						>
							<el-image v-if="imageUrl" :src="imageUrl" class="preview-image" fit="contain" />
							<div v-else class="uploader-content"> 
								<el-icon class="upload-icon">
									<Plus />
								</el-icon>
								<div class="upload-text">点击上传图片</div>
							</div>
						</el-upload>
					</el-card>
				</el-col>

				<!-- 预测结果图 -->
				<el-col :span="8">
					<el-card shadow="hover" class="card">
						<div class="image-title">预测结果</div>
						<el-image
							v-if="predictedImageUrl"
							:src="predictedImageUrl"
							class="preview-image"
							fit="contain"
						/>
						<div v-else class="placeholder">
							<el-icon>
								<Picture />
							</el-icon>
							<span>预测后将在此显示结果</span>
						</div>
					</el-card>
				</el-col>

				<!-- 智能建议 -->
				<el-col :span="8">
					<el-card shadow="hover" class="card">
						<div class="image-title">智能建议</div>
						<div class="suggestion-content" v-if="state.aiSuggestion">
							<div class="suggestion-text">{{ state.aiSuggestion }}</div>
						</div>
						<div v-else-if="state.suggestionLoading" class="placeholder">
							<el-icon class="is-loading">
								<Loading />
							</el-icon>
							<span>正在生成智能建议...</span>
						</div>
						<div v-else class="placeholder">
							<el-icon>
								<ChatLineRound />
							</el-icon>
							<span>预测完成后将自动生成智能建议</span>
						</div>
					</el-card>
				</el-col>
			</el-row>

			<el-row class="result-section">
				<el-col :span="24">
					<el-card>
						<div class="bottom" v-if="state.predictionResult.label">
							<div class="result-column">
								<div class="result-title">识别结果：</div>
								<div v-for="(label, index) in formatLabelArray(state.predictionResult.label)" :key="index" class="result-item">
									<span class="result-value">{{ label }}</span>
								</div>
							</div>
							<div class="result-column">
								<div class="result-title">预测概率：</div>
								<div v-for="(conf, index) in formatConfidenceArray(state.predictionResult.confidence)" :key="index" class="result-item">
									<span class="result-value">{{ conf }}</span>
								</div>
							</div>
							<div class="result-column">
								<div class="result-title">总时间：</div>
								<div class="result-item">
									<span class="result-value">{{ formatTime(state.predictionResult.allTime) }}</span>
								</div>
							</div>
						</div>
						<div class="bottom placeholder" v-else>
							<div style="width: 100%; text-align: center; color: #909399;">
								<el-icon style="margin-right: 8px; vertical-align: middle;"><Picture /></el-icon>
								<span>预测结果将在这里显示</span>
							</div>
						</div>
					</el-card>
				</el-col>
			</el-row>
		</div>
	</div>
</template>


<script setup lang="ts" name="imgPredict">
import { reactive, ref } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { Plus, ChatLineRound, Picture, Loading } from '@element-plus/icons-vue';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import axios from 'axios';

const imageUrl = ref('');
const conf = ref(50);
const uploadFile = ref<UploadInstance>();
const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);
const predictedImageUrl = ref('');

const state = reactive({
	img: '',
	predictionResult: {
		label: '',
		confidence: '',
		allTime: '',
	},
	form: {
		username: '',
		inputImg: '',
		conf: 0.5,
	},
	aiSuggestion: '',
	suggestionLoading: false,
	predictLoading: false,
});

const formatTooltip = (val: number) => {
	return (val / 100).toFixed(2);
};

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	if (response.code === 0) {
		imageUrl.value = URL.createObjectURL(uploadFile.raw!);
		state.img = response.data;
		ElMessage.success('图片上传成功');
	} else {
		ElMessage.error('图片上传失败');
	}
};

const upData = () => {
	if (!state.img) {
		ElMessage.warning('请先上传图片');
		return;
	}

	state.predictLoading = true;
	state.form.conf = conf.value / 100;
	state.form.username = userInfos.value.userName;
	state.form.inputImg = state.img;

	request.post('/api/flask/predict', state.form).then((res) => {
		state.predictLoading = false;

		if (res.code === 0) {
			try {
				const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;

				// 处理标签
				if (typeof data.label === 'string') {
					data.label = JSON.parse(data.label);
				}

				if (Array.isArray(data.label)) {
					state.predictionResult.label = data.label.map((item: string) =>
						item.replace(/\\u([\dA-Fa-f]{4})/g, (_, code) =>
							String.fromCharCode(parseInt(code, 16))
						)
					);
				}

				state.predictionResult.confidence = data.confidence;
				state.predictionResult.allTime = data.allTime;

				// 显示预测结果图片
				if (data.outImg) {
					predictedImageUrl.value = data.outImg;
				}

				ElMessage.success('预测成功！');

				// 自动获取AI建议
				getAISuggestion();
			} catch (error) {
				console.error('解析结果时出错:', error);
				ElMessage.error('预测结果解析失败');
			}
		} else {
			ElMessage.error(res.msg || '预测失败');
		}
	}).catch((error) => {
		state.predictLoading = false;
		console.error('预测请求失败:', error);
		ElMessage.error('预测请求失败，请检查网络连接');
	});
};

// 获取AI建议
const getAISuggestion = async () => {
	if (!state.predictionResult.label) {
		return;
	}
	
	state.suggestionLoading = true;
	try {
		const apiKey = ''; // 请替换为您的DeepSeek API密钥
		
		const labels = Array.isArray(state.predictionResult.label)
			? state.predictionResult.label.join(', ')
			: state.predictionResult.label;

		const prompt = `作为一个专业的农作物病害专家，请对以下情况进行详细分析：

1. 基本信息：
- 检测到的病害：${labels}
- 检测置信度：${state.predictionResult.confidence}

2. 请提供以下方面的专业分析：
(1) 病害危害程度：
1. 当前病害的严重程度评估
2. 对作物生长的影响
3. 可能造成的产量损失

(2) 防治建议：
1. 立即可采取的防治措施
2. 推荐使用的农药或生物防治方法
3. 施药注意事项和防护措施

(3) 预防措施：
1. 日常管理建议
2. 环境控制要点
3. 预防性保护措施

请用专业但易懂的语言回答，并尽可能提供具体的操作建议。`;

		const response = await axios.post('https://api.deepseek.com/v1/chat/completions', {
			model: 'deepseek-chat',
			messages: [{
				role: 'user',
				content: prompt
			}],
			stream: false
		}, {
			headers: {
				'Authorization': `Bearer ${apiKey}`,
				'Content-Type': 'application/json'
			}
		});

		state.aiSuggestion = response.data.choices[0].message.content;
	} catch (error) {
		console.error('获取AI建议出错:', error);
		state.aiSuggestion = '抱歉，暂时无法生成智能建议，请稍后重试。';
	} finally {
		state.suggestionLoading = false;
	}
};

// 格式化函数
const formatLabelArray = (label: any) => {
	if (Array.isArray(label)) {
		return label.map(item => item.replace(/[\[\]"]/g, '').trim());
	} else if (typeof label === 'string') {
		return [label.replace(/[\[\]"]/g, '').trim()];
	}
	return ['未知'];
};

const formatConfidenceArray = (confidence: string) => {
	if (!confidence) return ['0%'];
	try {
		let confidences = confidence;
		if (typeof confidence === 'string') {
			confidences = JSON.parse(confidence);
		}
		if (Array.isArray(confidences)) {
			return confidences.map(conf => {
				const confValue = parseFloat(String(conf).replace(/[\[\]"%]/g, ''));
				return confValue.toFixed(2) + '%';
			});
		} else {
			const confValue = parseFloat(String(confidence).replace(/[\[\]"%]/g, ''));
			return [confValue.toFixed(2) + '%'];
		}
	} catch (error) {
		console.error('解析置信度出错:', error);
		return ['0%'];
	}
};

const formatTime = (time: string) => {
	if (!time) return '0秒';
	return parseFloat(time).toFixed(3) + '秒';
};
</script>

<style scoped lang="scss">
.system-predict-container {
	width: 100%;
	height: 100vh;
	display: flex;
	flex-direction: column;
	overflow-y: auto;
	background: #f5f7fa;

	.system-predict-padding {
		padding: 15px;
		padding-bottom: 0;
		padding-top: 0;  /* 移除顶部内边距 */
		min-height: calc(100vh - 60px);
	}
}

.header {
	width: 100%;
	padding: 10px 0;
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: 15px;
	margin-bottom: 1px;
	background: white;
	padding: 10px;
	border-radius: 8px;
	box-shadow: none;  /* 移除阴影 */
}

.image-display {
	margin-top: 15px;

	.card {
		height: 100%;
		background: white;
		border-radius: 8px;
		box-shadow: none;
		transition: all 0.3s ease;
		
		&:hover {
			transform: none;
			box-shadow: none;
		}

		.image-title {
			font-size: 16px;
			font-weight: 600;
			color: #303133;
			margin-bottom: 15px;
			padding-bottom: 10px;
			border-bottom: 1px solid #ebeef5;
		}

		.avatar-uploader {
			width: 100%;
			height: 358px;
			border: 1px dashed #d9d9d9;
			border-radius: 4px;
			cursor: pointer;
			position: relative;
			overflow: hidden;
			transition: var(--el-transition-duration-fast);
			display: flex;
			justify-content: center;
			align-items: center;

			&:hover {
				border-color: var(--el-color-primary);
			}
		}

		.preview-image {
			width: 100%;
			height: 358px;
			object-fit: contain;
		}

		.uploader-content {
			width: 100%;
			height: 100%;
			display: flex;
			flex-direction: column;
			justify-content: center;
			align-items: center;
			gap: 10px;
		}

		.upload-icon {
			font-size: 28px;
			color: #909399;
		}

		.upload-text {
			color: #909399;
			font-size: 14px;
		}

		.placeholder {
			height: 358px;
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
			gap: 10px;
			color: #909399;

			.el-icon {
				font-size: 28px;
			}
		}

		.suggestion-content {
			height: 358px;
			padding: 15px;
			overflow-y: auto;
			background: #f5f7fa;
			border-radius: 4px;

			.suggestion-text {
				font-size: 14px;
				line-height: 1.8;
				color: #303133;
				white-space: pre-wrap;
				text-align: justify;
			}

			&::-webkit-scrollbar {
				width: 6px;
			}

			&::-webkit-scrollbar-thumb {
				background-color: #dcdfe6;
				border-radius: 3px;
			}

			&::-webkit-scrollbar-track {
				background-color: #f8f9fa;
			}
		}
	}
}
.result-section {
	margin-top: 10px;
	padding: 0;

	:deep(.el-card) {
		background: white;
		border-radius: 8px;
		box-shadow: none;
		margin: 0;
		
		.el-card__body {
			padding: 0;
		}
	}

	.bottom {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		padding: 15px 20px;
		background: white;
		border-radius: 8px;
		min-height: 115px;

		.result-column {
			width: 33%;
			padding: 0 15px;
			border-right: 1px solid #ebeef5;

			&:last-child {
				border-right: none;
			}

			.result-title {
				font-size: 14px;
				color: #606266;
				font-weight: normal;
				margin-bottom: 10px;
			}

			.result-item {
				margin: 5px 0;
				
				.result-value {
					color: #409EFF;
					font-weight: 500;
				}
			}
		}

		&.placeholder {
			color: #909399;
			justify-content: center;
			align-items: center;
			
			.el-icon {
				margin-right: 8px;
				font-size: 16px;
			}
		}
	}
}

.predict-button {
	background: linear-gradient(45deg, #409eff, #36a2f1);
	border: none;
	box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
	transition: all 0.3s ease;


	&:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
	}
}
</style>