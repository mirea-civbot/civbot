import React from 'react';
import { Box } from '@mui/material';
import ChatMessage from './ChatMessage';
import { Message } from '@/types/chat';

interface ChatWindowProps {
  messages: Message[];
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages }) => {
  return (
	<Box
	  sx={{
		flexGrow: 1,
		display: 'flex',
		flexDirection: 'column',
		overflowY: 'auto',
		p: 2,
		bgcolor: 'background.paper',
	  }}
	>
	  {messages.map((message) => (
		<ChatMessage key={message.id} message={message} />
	  ))}
	</Box>
  );
};

export default ChatWindow;
