import React from 'react';
import { List, ListItem, ListItemButton, ListItemText, Divider, Typography } from '@mui/material';
import { Dialog } from '@/types/chat';
import { Box } from '@mui/material';

interface DialogListProps {
  dialogs: Dialog[];
  selectedDialogId: string | null;
  onSelectDialog: (id: string) => void;
}

const DialogList: React.FC<DialogListProps> = ({ dialogs, selectedDialogId, onSelectDialog }) => {
  return (
    <Box sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        Dialogs
      </Typography>
      <Divider />
      <List>
        {dialogs.map((dialog) => (
          <ListItem key={dialog.id} disablePadding>
            <ListItemButton
              selected={selectedDialogId === dialog.id}
              onClick={() => onSelectDialog(dialog.id)}
            >
              <ListItemText
                primary={dialog.title}
                secondary={dialog.lastMessage}
                secondaryTypographyProps={{
                  noWrap: true,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default DialogList;
