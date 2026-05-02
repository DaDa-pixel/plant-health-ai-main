<template>
	<div class="dialog-wrapper">
		<el-dialog
			:title="state.dialog.title"
			v-model="state.dialog.isShowDialog"
			width="700px"
			:close-on-click-modal="false"
			class="custom-dialog"
		>
			<!-- 圆形头像上传 -->
			<div class="avatar-section">
				<el-upload
					ref="uploadFile"
					class="avatar-uploader"
					action="/api/files/upload"
					:show-file-list="false"
					:on-success="handleAvatarSuccessone"
				>
					<div class="avatar-circle" :class="{ 'has-img': imageUrl }">
						<img v-if="imageUrl" :src="imageUrl" class="avatar-img" />
						<div v-else class="avatar-placeholder">
							<el-icon class="upload-icon"><Plus /></el-icon>
							<span>上传头像</span>
						</div>
					</div>
				</el-upload>
			</div>

			<el-form ref="roleDialogFormRef" :model="state.form" size="default" label-width="90px" :rules="rules" class="custom-form">
				<el-row :gutter="24">
					<el-col :xs="24" :sm="12">
						<el-form-item label="账号" prop="username">
							<el-input v-model="state.form.username" placeholder="请输入账号" clearable>
								<template #prefix><el-icon><User /></el-icon></template>
							</el-input>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12">
						<el-form-item label="密码" prop="password">
							<el-input v-model="state.form.password" placeholder="请输入密码" clearable
								:type="showPassword ? 'text' : 'password'">
								<template #prefix><el-icon><Lock /></el-icon></template>
								<template #suffix>
									<el-icon class="eye-icon" @click="showPassword = !showPassword">
										<View v-if="showPassword" />
										<Hide v-else />
									</el-icon>
								</template>
							</el-input>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12">
						<el-form-item label="姓名" prop="name">
							<el-input v-model="state.form.name" placeholder="请输入姓名" clearable>
								<template #prefix><el-icon><EditPen /></el-icon></template>
							</el-input>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12">
						<el-form-item label="性别" prop="sex">
							<el-select v-model="state.form.sex" placeholder="请选择性别" style="width: 100%">
								<el-option label="男" value="男">
									<el-icon style="color:#409eff;vertical-align:middle;margin-right:4px;"><Male /></el-icon>男
								</el-option>
								<el-option label="女" value="女">
									<el-icon style="color:#f56c6c;vertical-align:middle;margin-right:4px;"><Female /></el-icon>女
								</el-option>
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12">
						<el-form-item label="邮箱" prop="email">
							<el-input v-model="state.form.email" placeholder="请输入邮箱" clearable>
								<template #prefix><el-icon><Message /></el-icon></template>
							</el-input>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12">
						<el-form-item label="手机号码" prop="tel">
							<el-input v-model="state.form.tel" placeholder="请输入手机号码" clearable>
								<template #prefix><el-icon><Phone /></el-icon></template>
							</el-input>
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="角色" prop="role">
							<el-select v-model="state.form.role" placeholder="请选择角色" style="width: 100%">
								<el-option v-for="item in option" :key="item.id" :label="item.label" :value="item.role" />
							</el-select>
						</el-form-item>
					</el-col>
				</el-row>
			</el-form>

			<template #footer>
				<div class="dialog-footer">
					<el-button class="btn-cancel" @click="onCancel">
						<el-icon><Close /></el-icon> 取 消
					</el-button>
					<el-button type="primary" class="btn-submit" @click="onSubmit">
						<el-icon><Check /></el-icon> {{ state.dialog.submitTxt }}
					</el-button>
				</div>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="systemRoleDialog">
import { nextTick, reactive, ref } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';
import {
	Plus, View, Hide, User, Lock, EditPen,
	Male, Female, Message, Phone, Close, Check
} from '@element-plus/icons-vue';
import request from '/@/utils/request';

const emit = defineEmits(['refresh']);

const imageUrl = ref('');
const uploadFile = ref<UploadInstance>();
const showPassword = ref(false);

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	// 本地预览：用上传的原始文件生成临时 URL
	imageUrl.value = URL.createObjectURL(uploadFile.raw!);
	// 保存后端返回的文件路径
	state.form.avatar = response.data;
};

const option = [
	{ id: 1, label: '管理员', role: 'admin' },
	{ id: 2, label: '普通用户', role: 'common' },
];

const roleDialogFormRef = ref();
const rules = {
	username: [
		{ required: true, message: '请输入账号', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
	],
	password: [
		{ required: true, message: '请输入密码', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
	],
	name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
	sex: [{ required: true, message: '请选择性别', trigger: 'change' }],
	email: [
		{ required: true, message: '请输入邮箱', trigger: 'blur' },
		{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
	],
	tel: [{ required: true, message: '请输入手机号码', trigger: 'blur' }],
	role: [{ required: true, message: '请选择角色', trigger: 'change' }]
};

const state = reactive({
	form: {} as any,
	menuData: [] as TreeType[],
	menuProps: { children: 'children', label: 'label' },
	submitTxt: '',
	dialog: { isShowDialog: false, type: '', title: '', submitTxt: '' },
});

const openDialog = (type: string, row: any) => {
	showPassword.value = false;
	if (type === 'edit') {
		state.form = { ...row };
		state.dialog.title = '修改信息';
		state.dialog.submitTxt = '修 改';
		imageUrl.value = state.form.avatar;
		if (row.id) {
			request.get('/api/user/detail/' + row.id).then((res) => {
				if (res.code == 0 && res.data) {
					state.form.password = res.data.password;
				}
			}).catch(() => {});
		}
	} else {
		state.dialog.title = '新增信息';
		state.dialog.submitTxt = '新 增';
		state.form = {} as any;
		nextTick(() => {
			uploadFile.value?.clearFiles();
			imageUrl.value = '';
		});
	}
	state.dialog.isShowDialog = true;
};

const closeDialog = () => { state.dialog.isShowDialog = false; };
const onCancel = () => { closeDialog(); };

const onSubmit = () => {
	if (!roleDialogFormRef.value) return;
	roleDialogFormRef.value.validate((valid: boolean) => {
		if (!valid) {
			ElMessage.error('请完善必填信息');
			return false;
		}
		if (state.form['role'] == '管理员') state.form['role'] = 'admin';
		else if (state.form['role'] == '普通用户') state.form['role'] = 'common';
		else if (state.form['role'] == '其他用户') state.form['role'] = 'others';

		const req = state.dialog.title == '修改信息'
			? request.post('/api/user/update', state.form)
			: request.post('/api/user', state.form);

		req.then((res) => {
			if (res.code == 0) {
				ElMessage.success(state.dialog.title == '修改信息' ? '修改成功！' : '添加成功！');
				setTimeout(() => { closeDialog(); emit('refresh'); }, 500);
			} else {
				ElMessage({ type: 'error', message: res.msg });
			}
		});
	});
};

defineExpose({ openDialog });
</script>

<style scoped lang="scss">
.dialog-wrapper {
	:deep(.custom-dialog) {
		border-radius: 16px;
		overflow: hidden;

		.el-dialog__header {
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			margin: 0;
			padding: 18px 24px;

			.el-dialog__title {
				color: #fff;
				font-size: 18px;
				font-weight: 600;
				letter-spacing: 1px;
			}

			.el-dialog__headerbtn .el-dialog__close {
				color: rgba(255,255,255,.8);
				font-size: 18px;
				&:hover { color: #fff; }
			}
		}

		.el-dialog__body { padding: 28px 36px 16px; }
		.el-dialog__footer { padding: 0 36px 22px; border: none; }
	}
}

/* 圆形头像 */
.avatar-section {
	display: flex;
	justify-content: center;
	margin-bottom: 24px;
}

.avatar-circle {
	width: 100px;
	height: 100px;
	border-radius: 50%;
	border: 3px dashed #dcdfe6;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	transition: all .3s;
	background: #f5f7fa;
	cursor: pointer;

	&.has-img {
		border-style: solid;
		border-color: #667eea;
		box-shadow: 0 4px 14px rgba(102,126,234,.3);
	}

	&:hover {
		border-color: #667eea;
		.avatar-placeholder { color: #667eea; }
	}
}

.avatar-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.avatar-placeholder {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 2px;
	color: #909399;
	font-size: 11px;
	transition: color .3s;
	.upload-icon { font-size: 24px; }
}

/* 表单 */
.custom-form {
	:deep(.el-form-item) {
		margin-bottom: 18px;

		.el-form-item__label {
			font-weight: 500;
			color: #606266;
		}

		.el-input__wrapper {
			border-radius: 10px;
			background: #f5f7fa;
			box-shadow: none;
			border: 1px solid transparent;
			transition: all .3s;

			&:hover, &.is-focus {
				background: #fff;
				border-color: #667eea;
				box-shadow: 0 0 0 3px rgba(102,126,234,.1);
			}
		}
	}

	.eye-icon {
		cursor: pointer;
		font-size: 18px;
		color: #909399;
		transition: color .3s;
		&:hover { color: #667eea; }
	}
}

/* 底部按钮 */
.dialog-footer {
	display: flex;
	justify-content: center;
	gap: 16px;
}

.btn-cancel {
	border-radius: 10px;
	padding: 8px 28px;
	font-weight: 500;
	transition: all .3s;
	&:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,.08); }
}

.btn-submit {
	border-radius: 10px;
	padding: 8px 28px;
	font-weight: 600;
	background: linear-gradient(135deg, #667eea, #764ba2);
	border: none;
	transition: all .3s;
	letter-spacing: 1px;
	&:hover {
		transform: translateY(-1px);
		box-shadow: 0 6px 20px rgba(102,126,234,.4);
	}
}
</style>
