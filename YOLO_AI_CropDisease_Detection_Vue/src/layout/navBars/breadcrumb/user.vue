<template>
	<div class="layout-navbars-breadcrumb-user pr15" :style="{ flex: layoutUserFlexNum }">
		<el-dropdown :show-timeout="70" :hide-timeout="50" trigger="click" @command="onComponentSizeChange" class="custom-dropdown">
			<div class="layout-navbars-breadcrumb-user-icon">
				<i class="iconfont icon-ziti" :title="t('message.user.title0')"></i>
			</div>
			<template #dropdown>
				<el-dropdown-menu>
					<el-dropdown-item command="large" :disabled="state.disabledSize === 'large'">{{ t('message.user.dropdownLarge') }}</el-dropdown-item>
					<el-dropdown-item command="default" :disabled="state.disabledSize === 'default'">{{ t('message.user.dropdownDefault') }}</el-dropdown-item>
					<el-dropdown-item command="small" :disabled="state.disabledSize === 'small'">{{ t('message.user.dropdownSmall') }}</el-dropdown-item>
				</el-dropdown-menu>
			</template>
		</el-dropdown>
		<div class="layout-navbars-breadcrumb-user-icon" @click="onSearchClick">
			<el-icon :title="t('message.user.title2')">
				<SearchIcon />
			</el-icon>
		</div>
		<div class="layout-navbars-breadcrumb-user-icon" @click="onLayoutSetingClick">
			<i class="icon-skin iconfont" :title="t('message.user.title3')"></i>
		</div>
		<div class="layout-navbars-breadcrumb-user-icon mr10" @click="onScreenfullClick">
			<i
				class="iconfont"
				:title="state.isScreenfull ? t('message.user.title6') : t('message.user.title5')"
				:class="!state.isScreenfull ? 'icon-fullscreen' : 'icon-tuichuquanping'"
			></i>
		</div>
		<el-dropdown :show-timeout="70" :hide-timeout="50" @command="onHandleCommandClick" class="custom-dropdown">
			<span class="layout-navbars-breadcrumb-user-link">
				<img :src="state.img || userInfos.photo" alt="用户头像" class="layout-navbars-breadcrumb-user-link-photo mr5" />
				{{ username }}
				<el-icon class="el-icon--right">
					<ArrowDown />
				</el-icon>
			</span>
			<template #dropdown>
				<el-dropdown-menu>
					<el-dropdown-item command="/">{{ t('message.user.dropdown1') }}</el-dropdown-item>
					<el-dropdown-item divided command="logOut">{{ t('message.user.dropdown5') }}</el-dropdown-item>
				</el-dropdown-menu>
			</template>
		</el-dropdown>
		<Search ref="searchRef" />
	</div>
</template>

<script setup lang="ts" name="layoutBreadcrumbUser">
import { defineAsyncComponent, ref, computed, reactive, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessageBox, ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useUserInfo } from '/@/stores/userInfo';
import { useThemeConfig } from '/@/stores/themeConfig';
import other from '/@/utils/other';
import request from '/@/utils/request';
import { Session, Local } from '/@/utils/storage';
import screenfull from 'screenfull';
import mittBus from '/@/utils/mitt';
import { Search as SearchIcon, ArrowDown } from '@element-plus/icons-vue';
const Search = defineAsyncComponent(() => import('/@/layout/navBars/breadcrumb/search.vue'));

const { locale, t } = useI18n();
const router = useRouter();
const stores = useUserInfo();
const storesThemeConfig = useThemeConfig();
const { userInfos } = storeToRefs(stores);
const { themeConfig } = storeToRefs(storesThemeConfig);
const searchRef = ref();
const state = reactive({
	img: '',
	isScreenfull: false,
	disabledI18n: 'zh-cn',
	disabledSize: 'large',
});

let username = '';

const layoutUserFlexNum = computed(() => {
	const { layout, isClassicSplitMenu } = themeConfig.value;
	const layoutArr = ['defaults', 'columns'];
	if (layoutArr.includes(layout) || (layout === 'classic' && !isClassicSplitMenu)) return '1';
	return '';
});

const onLayoutSetingClick = () => {
	mittBus.emit('openSetingsDrawer');
};

const onHandleCommandClick = (path: string) => {
	if (path === 'logOut') {
		ElMessageBox({
			closeOnClickModal: false,
			closeOnPressEscape: false,
			title: t('message.user.logOutTitle'),
			message: t('message.user.logOutMessage'),
			showCancelButton: true,
			confirmButtonText: t('message.user.logOutConfirm'),
			cancelButtonText: t('message.user.logOutCancel'),
			buttonSize: 'default',
			beforeClose: (action, instance, done) => {
				if (action === 'confirm') {
					instance.confirmButtonLoading = true;
					instance.confirmButtonText = t('message.user.logOutExit');
					setTimeout(() => {
						done();
						setTimeout(() => {
							instance.confirmButtonLoading = false;
						}, 300);
					}, 700);
				} else {
					done();
				}
			},
		})
			.then(async () => {
				Session.clear();
				window.location.reload();
			})
			.catch(() => {});
	} else {
		router.push(path);
	}
};

const onSearchClick = () => {
	searchRef.value.openSearch();
};

const onComponentSizeChange = (size: string) => {
	Local.remove('themeConfig');
	themeConfig.value.globalComponentSize = size;
	Local.set('themeConfig', themeConfig.value);
	initI18nOrSize('globalComponentSize', 'disabledSize');
	window.location.reload();
};

const onScreenfullClick = () => {
	if (!screenfull.isEnabled) {
		ElMessage.warning('暂不不支持全屏');
		return false;
	}
	screenfull.toggle();
	screenfull.on('change', () => {
		state.isScreenfull = screenfull.isFullscreen;
	});
};

const onLanguageChange = (lang: string) => {
	Local.remove('themeConfig');
	themeConfig.value.globalI18n = lang;
	Local.set('themeConfig', themeConfig.value);
	locale.value = lang;
	other.useTitle();
	initI18nOrSize('globalI18n', 'disabledI18n');
};

const initI18nOrSize = (value: string, attr: string) => {
	state[attr] = Local.get('themeConfig')[value];
};

const getTableData = () => {
	if (!userInfos.value.userName) return;

	request.get('/api/user/' + userInfos.value.userName).then((res) => {
		if (res.code == 0 && res.data) {
			state.img = res.data.avatar || userInfos.value.photo;

			if (res.data.avatar) {
				userInfos.value.photo = res.data.avatar;
				Session.set('userInfo', userInfos.value);
			}
		} else {
			ElMessage({
				type: 'error',
				message: res.msg,
			});
		}
	});
};

watch(() => userInfos.value.photo, (newPhoto) => {
	if (newPhoto) {
		state.img = newPhoto;
	}
}, { immediate: true });

onMounted(() => {
	username = userInfos.value.userName;
	getTableData();
	if (Local.get('themeConfig')) {
		initI18nOrSize('globalComponentSize', 'disabledSize');
		initI18nOrSize('globalI18n', 'disabledI18n');
	}
});
</script>

<style scoped lang="scss">
.tile {
	width: 100%;
	height: 100%;
	color: black;
	font-size: 20px;
	font-weight: 600;
	margin-left: -150px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
	text-align: center;
}
.layout-navbars-breadcrumb-user {
	display: flex;
	align-items: center;
	justify-content: flex-end;
	&-link {
		height: 100%;
		display: flex;
		align-items: center;
		white-space: nowrap;
		&-photo {
			width: 40px;
			height: 40px;
			border-radius: 100%;
			margin-right: 15px;
		}
	}
	&-icon {
		padding: 0 10px;
		cursor: pointer;
		color: #000000 !important;
		height: 50px;
		line-height: 50px;
		display: flex;
		align-items: center;
		&:hover {
			background: #f0f0f0 !important;
			i {
				display: inline-block;
			}
		}
		i {
			font-size: 16px;
		}
	}
	:deep(.el-dropdown) {
		color: var(--next-bg-topBarColor);
	}
	:deep(.el-badge) {
		height: 40px;
		line-height: 40px;
		display: flex;
		align-items: center;
	}
	:deep(.el-badge__content.is-fixed) {
		top: 12px;
	}
}
.custom-dropdown {
	/* 自定义 el-dropdown 的样式 */
	.el-dropdown-link {
		color: #fff; /* 修改字体颜色 */
		background-color: #409eff; /* 修改背景色 */
		padding: 10px 20px;
		border-radius: 4px;
		transition: background-color 0.3s, box-shadow 0.3s;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		cursor: pointer;
	}

	.el-dropdown-link:hover {
		background-color: #66b1ff; /* 悬停时的背景色 */
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
	}

	.el-dropdown-menu {
		background-color: #ffffff;
		border: 1px solid #dcdcdc;
		border-radius: 10px;
		box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
		overflow: hidden;
		padding: 5px;
	}

	.el-dropdown-item {
		color: #000000 !important;
		padding: 12px 20px;
		transition: background-color 0.3s, color 0.3s;
		display: flex;
		align-items: center;
		justify-content: center;
		&:hover {
			background-color: #f0f0f0 !important;
		}
	}

	.el-dropdown-item i {
		margin-right: 8px;
	}

	.el-dropdown-item:active {
		background-color: #e6f7ff;
	}
}
</style>
