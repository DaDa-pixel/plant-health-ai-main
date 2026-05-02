import { io } from 'socket.io-client';

export class SocketService {
  private socket;

  constructor() {
    // 使用相对路径，通过 Vite 代理连接 Flask WebSocket
    // 开发时 connecting to same host:port, proxy forwards /socket.io/ to Flask
    const protocol = window.location.protocol;
    const host = window.location.host;
    this.socket = io(`${protocol}//${host}`, {
      path: '/flask/socket.io'
    });
  }

  on(event: string, callback: Function) {
    this.socket.on(event, (data) => callback(data.data));
  }

  emit(event: string, data: any) {
    this.socket.emit(event, data);
  }

  disconnect() {
    this.socket.disconnect();
  }
}