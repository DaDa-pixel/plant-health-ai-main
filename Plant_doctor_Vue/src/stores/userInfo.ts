import { defineStore } from 'pinia';
import Cookies from 'js-cookie';
import { Session } from '/@/utils/storage';
import request from '/@/utils/request';

export const useUserInfo = defineStore('userInfo', {
	state: (): UserInfosState => ({
		userInfos: {
			userName: '',
			userNickname: '',
			role: '',
			photo: '',
			time: 0,
			roles: [],
			authBtnList: [],
		},
	}),
	actions: {
		async setUserInfos() {
			if (Session.get('userInfo')) {
				const cached = Session.get('userInfo');
				// 如果缓存中没有真实姓名，从后端获取
				if (!cached.userNickname) {
					const fresh = await this.getApiUserInfo();
					this.userInfos = fresh;
				} else {
					this.userInfos = cached;
				}
			} else {
				const userInfos: any = await this.getApiUserInfo();
				this.userInfos = userInfos;
			}
		},
		async getApiUserInfo() {
			const userName = Cookies.get('userName');
			const userNickname = Cookies.get('userNickname') || userName;
			const role = Cookies.get('role');
			
			let defaultRoles: Array<string> = [];
			let defaultAuthBtnList: Array<string> = [];
			
			let adminRoles: Array<string> = ['admin'];
			let adminAuthBtnList: Array<string> = ['btn.add', 'btn.del', 'btn.edit', 'btn.link'];
			let commonRoles: Array<string> = ['common'];
			let commonAuthBtnList: Array<string> = ['btn.add', 'btn.link'];
			
			if (role === 'admin') {
				defaultRoles = adminRoles;
				defaultAuthBtnList = adminAuthBtnList;
			} else if (role === 'common') {
				defaultRoles = commonRoles;
				defaultAuthBtnList = commonAuthBtnList;
			}

			const userInfos = {
				userName: userName,
				userNickname: userNickname,
				role: role,
				photo: '',
				time: new Date().getTime(),
				roles: defaultRoles,
				authBtnList: defaultAuthBtnList,
			};
			
			if (userName) {
				try {
					const res = await request.get('/api/user/' + userName);
					if (res.code === 0 && res.data) {
						userInfos.photo = res.data.avatar || userInfos.photo;
						// 从后端获取真实姓名（覆盖cookie默认值）
						if (res.data.name) {
							userInfos.userNickname = res.data.name;
						}
					}
				} catch (error) {
					console.error('获取用户信息失败:', error);
				}
			}
			
			Session.set('userInfo', userInfos);
			return userInfos;
		},
	},
});
