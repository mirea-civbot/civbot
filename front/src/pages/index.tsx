import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import DialogList from '@/components/Chat/DialogList';
import ChatWindow from '@/components/Chat/ChatWindow';
import ChatInput from '@/components/Chat/ChatInput';
import { Message, Dialog } from '@/types/chat';
import { Box } from '@mui/material';

const Home: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [dialogs, setDialogs] = useState<Dialog[]>([]);
  const [selectedDialogId, setSelectedDialogId] = useState<string | null>(null);

  // Mock data initialization
  useEffect(() => {
    const mockDialogs: Dialog[] = [
      {
        id: '1',
        title: 'General Chat',
        lastMessage: 'Hello! How can I help you?',
        timestamp: new Date(),
      },
      {
        id: '2',
        title: 'Technical Support',
        lastMessage: 'Please describe your issue',
        timestamp: new Date(Date.now() - 1000 * 60 * 60),
      },
    ];

    setDialogs(mockDialogs);
    setSelectedDialogId('1');

    const initialMessages: Message[] = [
      {
        id: '1',
        text: 'Hello! How can I help you?',
        sender: 'bot',
        timestamp: new Date(),
      },
    ];

    setMessages(initialMessages);
  }, []);

  const handleSendMessage = (text: string) => {
    const newUserMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);

    // Simulate bot response after 1 second
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: `I received your message: "${text}"`,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botResponse]);

      // Update last message in dialogs
      setDialogs((prev) =>
        prev.map((dialog) =>
          dialog.id === selectedDialogId
            ? { ...dialog, lastMessage: text, timestamp: new Date() }
            : dialog
        )
      );
    }, 1000);
  };

  const handleSelectDialog = (id: string) => {
    setSelectedDialogId(id);
    // In a real app, you would load messages for the selected dialog here
  };

  return (
    <Layout>
      <DialogList
        dialogs={dialogs}
        selectedDialogId={selectedDialogId}
        onSelectDialog={handleSelectDialog}
      />
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
        }}
      >
        <ChatWindow messages={messages} />
        <ChatInput onSendMessage={handleSendMessage} />
      </Box>
    </Layout>
  );
};

export default Home;
