<template>
	<div class="user-manage-container">
		<!-- 统计卡片 -->
		<div class="stat-cards">
			<div class="stat-card stat-card-total">
				<div class="stat-icon"><el-icon><User /></el-icon></div>
				<div class="stat-info">
					<span class="stat-num">{{ state.tableData.total }}</span>
					<span class="stat-label">用户总数</span>
				</div>
			</div>
			<div class="stat-card stat-card-admin">
				<div class="stat-icon"><el-icon><Monitor /></el-icon></div>
				<div class="stat-info">
					<span class="stat-num">{{ adminCount }}</span>
					<span class="stat-label">管理员</span>
				</div>
			</div>
			<div class="stat-card stat-card-user">
				<div class="stat-icon"><el-icon><UserFilled /></el-icon></div>
				<div class="stat-info">
					<span class="stat-num">{{ commonCount }}</span>
					<span class="stat-label">普通用户</span>
				</div>
			</div>
		</div>

		<!-- 主体卡片 -->
		<div class="main-card">
			<!-- 搜索与操作栏 -->
			<div class="toolbar">
				<div class="toolbar-left">
					<el-input
						v-model="state.tableData.param.search"
						placeholder="搜索用户名、姓名、手机号..."
						clearable
						class="search-input"
						@keyup.enter="getTableData()"
					>
						<template #prefix>
							<el-icon><Search /></el-icon>
						</template>
					</el-input>
					<el-button type="primary" class="btn-primary" @click="getTableData()">
						<el-icon><Search /></el-icon>
						查询
					</el-button>
				</div>
				<div class="toolbar-right">
					<el-button type="success" class="btn-add" @click="onOpenAddRole('add')">
						<el-icon><Plus /></el-icon>
						新增用户
					</el-button>
				</div>
			</div>

			<!-- 数据表格 -->
			<el-table
				:data="state.tableData.data"
				v-loading="state.tableData.loading"
				stripe
				border
				class="user-table"
				:header-cell-style="{
					background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
					color: '#fff',
					fontWeight: 600,
					border: 'none'
				}"
			>
				<el-table-column type="index" label="序号" width="70" align="center" />
				<el-table-column prop="username" label="账号" min-width="110" align="center">
					<template #default="scope">
						<div class="cell-username">
							<el-icon><User /></el-icon>
							<span>{{ scope.row.username }}</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="name" label="姓名" min-width="110" align="center">
					<template #default="scope">
						<span class="cell-name">{{ scope.row.name }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="sex" label="性别" width="80" align="center">
					<template #default="scope">
						<el-tag :type="scope.row.sex === '男' ? 'primary' : 'danger'" size="small" effect="plain">
							<el-icon style="margin-right: 3px;">
								<Male v-if="scope.row.sex === '男'" />
								<Female v-else />
							</el-icon>
							{{ scope.row.sex }}
						</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="email" label="邮箱" min-width="180" align="center">
					<template #default="scope">
						<span class="cell-email">{{ scope.row.email }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="tel" label="手机号码" width="140" align="center">
					<template #default="scope">
						<span class="cell-tel">{{ scope.row.tel }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="role" label="角色" width="120" align="center">
					<template #default="scope">
						<el-tag
							:type="scope.row.role === '管理员' ? 'danger' : scope.row.role === '普通用户' ? 'primary' : 'info'"
							size="default"
							effect="dark"
							class="role-tag"
						>
							<el-icon style="margin-right: 4px;">
								<StarFilled v-if="scope.row.role === '管理员'" />
								<UserFilled v-else />
							</el-icon>
							{{ scope.row.role }}
						</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="avatar" label="头像" width="90" align="center">
					<template #default="scope">
						<el-avatar
							:src="scope.row.avatar"
							:size="40"
							class="user-avatar"
							v-if="scope.row.avatar"
						/>
						<el-avatar
							:size="40"
							class="user-avatar"
							style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
							v-else
						>
							{{ scope.row.name?.charAt(0) || '?' }}
						</el-avatar>
					</template>
				</el-table-column>
				<el-table-column label="操作" width="180" align="center" fixed="right">
					<template #default="scope">
						<el-button size="small" class="btn-edit" @click="onOpenEditRole('edit', scope.row)">
							<el-icon><Edit /></el-icon>
							修改
						</el-button>
						<el-popconfirm
							title="确定要删除该用户吗？"
							confirm-button-text="确认删除"
							cancel-button-text="取消"
							@confirm="onRowDel(scope.row)"
						>
							<template #reference>
								<el-button size="small" type="danger" plain class="btn-delete">
									<el-icon><Delete /></el-icon>
									删除
								</el-button>
							</template>
						</el-popconfirm>
					</template>
				</el-table-column>
			</el-table>

			<!-- 分页 -->
			<div class="pagination-wrapper">
				<el-pagination
					@size-change="onHandleSizeChange"
					@current-change="onHandleCurrentChange"
					:pager-count="5"
					:page-sizes="[10, 20, 30]"
					v-model:current-page="state.tableData.param.pageNum"
					background
					v-model:page-size="state.tableData.param.pageSize"
					layout="total, sizes, prev, pager, next, jumper"
					:total="state.tableData.total"
				/>
			</div>
		</div>

		<RoleDialog ref="roleDialogRef" @refresh="getTableData()" />
	</div>
</template>

<script setup lang="ts" name="systemUser">
import { defineAsyncComponent, reactive, onMounted, ref } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import {
	Search, Plus, Edit, Delete, User, Monitor, UserFilled,
	Male, Female, StarFilled
} from '@element-plus/icons-vue';
import request from '/@/utils/request';

// 引入组件
const RoleDialog = defineAsyncComponent(() => import('./dialog.vue'));

// 定义变量内容
const roleDialogRef = ref();
const state = reactive({
	tableData: {
		data: [] as any,
		total: 0,
		loading: false,
		param: {
			search: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
});

// 管理员和普通用户总数（从接口获取）
const adminCount = ref(0);
const commonCount = ref(0);

const getTableData = () => {
	state.tableData.loading = true;
	request
		.get('/api/user', {
			params: state.tableData.param,
		})
		.then((res) => {
			if (res.code == 0) {
				state.tableData.data = [];
				setTimeout(() => {
					state.tableData.loading = false;
				}, 500);
				for (let i = 0; i < res.data.records.length; i++) {
					state.tableData.data[i] = res.data.records[i];
					state.tableData.data[i]['num'] = i + 1;
					if (state.tableData.data[i]['role'] == 'admin') {
						state.tableData.data[i]['role'] = '管理员';
					} else if (state.tableData.data[i]['role'] == 'common') {
						state.tableData.data[i]['role'] = '普通用户';
					} else if (state.tableData.data[i]['role'] == 'others') {
						state.tableData.data[i]['role'] = '其他用户';
					}
				}
				state.tableData.total = res.data.total;
				// 从接口读取总数统计
				adminCount.value = res.data.adminCount ?? 0;
				commonCount.value = res.data.commonCount ?? 0;
			} else {
				ElMessage({
					type: 'error',
					message: res.msg,
				});
			}
		});
};

// 打开新增角色弹窗
const onOpenAddRole = (type: string) => {
	roleDialogRef.value.openDialog(type);
};
// 打开修改角色弹窗
const onOpenEditRole = (type: string, row: Object) => {
	roleDialogRef.value.openDialog(type, row);
};

// 删除角色
const onRowDel = (row: any) => {
	request.delete('/api/user/' + row.id).then((res) => {
		if (res.code == 0) {
			ElMessage({
				type: 'success',
				message: '删除成功！',
			});
		} else {
			ElMessage({
				type: 'error',
				message: res.msg,
			});
		}
	});
	setTimeout(() => {
		getTableData();
	}, 500);
};
// 分页改变
const onHandleSizeChange = (val: number) => {
	state.tableData.param.pageSize = val;
	getTableData();
};
// 分页改变
const onHandleCurrentChange = (val: number) => {
	state.tableData.param.pageNum = val;
	getTableData();
};

// 页面加载时
onMounted(() => {
	getTableData();
});
</script>

<style scoped lang="scss">
.user-manage-container {
	padding: 20px;
	min-height: 100%;
	background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* ========== 统计卡片 ========== */
.stat-cards {
	display: flex;
	gap: 20px;
	margin-bottom: 20px;
}

.stat-card {
	flex: 1;
	display: flex;
	align-items: center;
	padding: 20px 24px;
	border-radius: 16px;
	background: #fff;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
	transition: all 0.3s ease;

	&:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
	}

	.stat-icon {
		width: 52px;
		height: 52px;
		border-radius: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 16px;
		font-size: 24px;
		color: #fff;
		flex-shrink: 0;
	}

	.stat-info {
		display: flex;
		flex-direction: column;

		.stat-num {
			font-size: 28px;
			font-weight: 700;
			line-height: 1.2;
		}

		.stat-label {
			font-size: 13px;
			color: #909399;
			margin-top: 2px;
		}
	}
}

.stat-card-total .stat-icon {
	background: linear-gradient(135deg, #667eea, #764ba2);
}
.stat-card-total .stat-num {
	color: #667eea;
}

.stat-card-admin .stat-icon {
	background: linear-gradient(135deg, #f093fb, #f5576c);
}
.stat-card-admin .stat-num {
	color: #f5576c;
}

.stat-card-user .stat-icon {
	background: linear-gradient(135deg, #4facfe, #00f2fe);
}
.stat-card-user .stat-num {
	color: #4facfe;
}

/* ========== 主体卡片 ========== */
.main-card {
	background: #fff;
	border-radius: 16px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
	padding: 20px;
}

/* ========== 工具栏 ========== */
.toolbar {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
	flex-wrap: wrap;
	gap: 12px;

	.toolbar-left {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.toolbar-right {
		display: flex;
		align-items: center;
		gap: 10px;
	}
}

.search-input {
	width: 240px;

	:deep(.el-input__wrapper) {
		border-radius: 10px;
		background: #f5f7fa;
		box-shadow: none;
		border: 1px solid transparent;
		transition: all 0.3s;

		&:hover,
		&.is-focus {
			background: #fff;
			border-color: #667eea;
			box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
		}
	}
}

.btn-primary {
	border-radius: 10px;
	background: linear-gradient(135deg, #667eea, #764ba2);
	border: none;
	padding: 8px 18px;
	transition: all 0.3s;

	&:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
	}
}

.btn-add {
	border-radius: 10px;
	background: linear-gradient(135deg, #43e97b, #38f9d7);
	border: none;
	color: #fff;
	padding: 8px 20px;
	font-weight: 600;
	transition: all 0.3s;

	&:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 15px rgba(67, 233, 123, 0.4);
		color: #fff;
	}
}

/* ========== 表格 ========== */
:deep(.user-table) {
	border-radius: 12px;
	overflow: hidden;
	border: none;

	.el-table__header-wrapper {
		border-radius: 12px 12px 0 0;
		overflow: hidden;
	}

	.el-table__body-wrapper {
		&::-webkit-scrollbar {
			width: 6px;
			height: 6px;
		}
		&::-webkit-scrollbar-thumb {
			background: #c0c4cc;
			border-radius: 3px;
		}
	}

	.el-table__row {
		transition: all 0.25s;

		&:hover {
			transform: translateY(-1px);
			box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
		}
	}

	.el-table__cell {
		padding: 14px 0;
	}
}

/* ========== 单元格样式 ========== */
.cell-username {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 6px;
	font-weight: 500;
	color: #303133;
}

.cell-name {
	font-weight: 500;
	color: #303133;
}

.cell-email {
	color: #606266;
	font-size: 13px;
}

.cell-tel {
	font-family: 'Courier New', monospace;
	color: #606266;
	letter-spacing: 0.5px;
}

.user-avatar {
	border: 2px solid #fff;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	transition: all 0.3s;

	&:hover {
		transform: scale(1.15);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
	}
}

.role-tag {
	padding: 0 14px;
	height: 28px;
	line-height: 28px;
	border-radius: 14px;
	font-weight: 500;
}

/* ========== 操作按钮 ========== */
.btn-edit {
	border-radius: 8px;
	color: #667eea;
	border-color: #667eea;
	transition: all 0.3s;
	padding: 5px 12px;

	&:hover {
		background: linear-gradient(135deg, #667eea, #764ba2);
		color: #fff;
		border-color: transparent;
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
	}
}

.btn-delete {
	border-radius: 8px;
	transition: all 0.3s;
	padding: 5px 12px;

	&:hover {
		background: linear-gradient(135deg, #f093fb, #f5576c);
		color: #fff;
		border-color: transparent;
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
	}
}

/* ========== 分页 ========== */
.pagination-wrapper {
	display: flex;
	justify-content: flex-end;
	margin-top: 20px;
	padding-top: 16px;
	border-top: 1px solid #f0f0f0;

	:deep(.el-pagination) {
		.el-pagination__total {
			color: #909399;
			font-weight: 500;
		}

		.btn-prev,
		.btn-next,
		.el-pager li {
			border-radius: 8px;
			margin: 0 2px;
			font-weight: 500;
			transition: all 0.3s;

			&:hover {
				color: #667eea;
			}

			&.is-active {
				background: linear-gradient(135deg, #667eea, #764ba2);
				color: #fff;
				border: none;
			}
		}

		.el-pagination__sizes .el-select .el-input .el-input__wrapper {
			border-radius: 8px;
		}
	}
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
	.user-manage-container {
		padding: 10px;
	}

	.stat-cards {
		flex-direction: column;
		gap: 12px;
	}

	.toolbar {
		flex-direction: column;

		.toolbar-left {
			width: 100%;

			.search-input {
				flex: 1;
			}
		}

		.toolbar-right {
			width: 100%;

			.btn-add {
				width: 100%;
			}
		}
	}
}
</style>
