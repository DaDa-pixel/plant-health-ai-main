import { defineStore } from 'pinia';
import Cookies from 'js-cookie';
import { Session } from '/@/utils/storage';
import request from '/@/utils/request';

export const useUserInfo = defineStore('userInfo', {
	state: (): UserInfosState => ({
		userInfos: {
			userName: '',
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
				this.userInfos = Session.get('userInfo');
			} else {
				const userInfos: any = await this.getApiUserInfo();
				this.userInfos = userInfos;
			}
		},
		async getApiUserInfo() {
			const userName = Cookies.get('userName');
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
					}
				} catch (error) {
					console.error('获取用户头像失败:', error);
				}
			}
			
			Session.set('userInfo', userInfos);
			return userInfos;
		},
	},
});
