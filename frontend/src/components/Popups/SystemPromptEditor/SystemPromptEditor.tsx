import React, { useState, useEffect } from 'react';
import { Button, Dialog, TextArea, Typography, Banner } from '@neo4j-ndl/react';
import { getSystemPrompt, updateSystemPrompt } from '../../../services/SystemPromptAPI';
import { showErrorToast, showSuccessToast } from '../../../utils/Toasts';

interface SystemPromptEditorProps {
  open: boolean;
  onClose: () => void;
}

const SystemPromptEditor: React.FC<SystemPromptEditorProps> = ({ open, onClose }) => {
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (open) {
      loadSystemPrompt();
    }
  }, [open]);

  const loadSystemPrompt = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await getSystemPrompt();
      if (response.status === 'Success') {
        setSystemPrompt(response.data.system_prompt);
      } else {
        setError('Failed to load system prompt');
      }
    } catch (error) {
      setError('Error loading system prompt');
      // console.error('Error loading system prompt:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError('');
      const response = await updateSystemPrompt(systemPrompt);
      if (response.status === 'Success') {
        showSuccessToast('System prompt updated successfully');
        onClose();
      } else {
        setError('Failed to update system prompt');
      }
    } catch (error) {
      setError('Error updating system prompt');
      // console.error('Error updating system prompt:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setSystemPrompt('');
    setError('');
    onClose();
  };

  return (
    <Dialog
      isOpen={open}
      onClose={handleCancel}
      size='unset'
      aria-labelledby='system-prompt-editor-dialog'
      modalProps={{
        className: 'h-[90vh] w-[90vw] max-w-[1400px] min-w-[800px]',
        id: 'system-prompt-editor-modal',
      }}
    >
      <Dialog.Header id='system-prompt-editor-dialog' className='flex-shrink-0'>
        <Typography variant='h4'>Edit System Prompt</Typography>
      </Dialog.Header>

      <Dialog.Content className='flex flex-col flex-1 min-h-0 p-4'>
        {error && <Banner type='danger' title='Error' description={error} className='mb-4 flex-shrink-0' />}

        <div className='flex-1 flex flex-col min-h-0'>
          <TextArea
            value={systemPrompt}
            placeholder={isLoading ? 'Loading system prompt...' : 'Enter your system prompt...'}
            className='w-full h-full font-mono text-sm flex-1 min-h-0'
            size='large'
            isFluid={true}
            htmlAttributes={{
              onChange: (e) => {
                // console.log('TextArea onChange triggered:', e.target.value);
                setSystemPrompt(e.target.value);
              },
              onFocus: () => {
                /* console.log('TextArea focused') */
              },
              onBlur: () => {
                /* console.log('TextArea blurred') */
              },
            }}
            style={{
              flex: 1,
              minHeight: '60vh',
              resize: 'none',
              overflow: 'auto',
              height: '100%',
            }}
          />
          {isLoading && <div className='text-sm text-gray-500 mt-2 flex-shrink-0'>Loading system prompt...</div>}
          <div className='text-xs text-gray-400 mt-2 flex-shrink-0'>Character count: {systemPrompt.length}</div>
        </div>
      </Dialog.Content>

      <Dialog.Actions className='flex-shrink-0 p-4 border-t border-palette-neutral-border-weak'>
        <div className='flex gap-3 justify-end w-full'>
          <Button variant='tertiary' onClick={handleCancel} disabled={isSaving} size='medium'>
            Cancel
          </Button>
          <Button
            variant='primary'
            onClick={handleSave}
            disabled={isLoading || isSaving}
            loading={isSaving}
            size='medium'
          >
            Save
          </Button>
        </div>
      </Dialog.Actions>
    </Dialog>
  );
};

export default SystemPromptEditor;
