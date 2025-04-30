export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export interface Dialog {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
}
