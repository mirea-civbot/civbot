import React from 'react';
import { Avatar, Box, Typography } from '@mui/material';
import { Message } from '@/types/chat';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
          alignItems: 'flex-end',
          maxWidth: '70%',
        }}
      >
        <Avatar
          sx={{
            bgcolor: message.sender === 'user' ? 'primary.main' : 'secondary.main',
            ml: message.sender === 'user' ? 2 : 0,
            mr: message.sender === 'bot' ? 2 : 0,
          }}
        >
          {message.sender === 'user' ? 'U' : 'B'}
        </Avatar>
        <Box
          sx={{
            bgcolor: message.sender === 'user' ? 'primary.light' : 'grey.200',
            color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
            p: 2,
            borderRadius: 2,
          }}
        >
          <Typography variant="body1">{message.text}</Typography>
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              textAlign: 'right',
              color: message.sender === 'user' ? 'primary.contrastText' : 'text.secondary',
            }}
          >
            {message.timestamp.toLocaleTimeString()}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatMessage;
