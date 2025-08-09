import React, { useState, useEffect } from 'react';
import { Button, Dialog, TextArea, Typography, Banner } from '@neo4j-ndl/react';
import {
  getSystemPromptSlot,
  updateSystemPromptSlot,
  getActiveSystemPromptSlot,
  setActiveSystemPromptSlot,
} from '../../../services/SystemPromptAPI';
import { showErrorToast, showSuccessToast } from '../../../utils/Toasts';

interface SystemPromptEditorProps {
  open: boolean;
  onClose: () => void;
}

interface PromptSlots {
  prompt_1: string;
  prompt_2: string;
  prompt_3: string;
}

const getSlotDisplayName = (slot: string): string => {
  switch (slot) {
    case 'prompt_1':
      return 'Prompt 1';
    case 'prompt_2':
      return 'Prompt 2';
    case 'prompt_3':
      return 'Prompt 3';
    default:
      return slot;
  }
};

const SystemPromptEditor: React.FC<SystemPromptEditorProps> = ({ open, onClose }) => {
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [currentSlot, setCurrentSlot] = useState<keyof PromptSlots>('prompt_1');
  const [activeSlot, setActiveSlot] = useState<string>('prompt_1');
  const [promptSlots, setPromptSlots] = useState<PromptSlots>({
    prompt_1: '',
    prompt_2: '',
    prompt_3: '',
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (open) {
      loadSystemPrompt();
      loadAllPromptSlots();
      loadActivePromptSlot();
    }
  }, [open]);

  const loadSystemPrompt = async () => {
    try {
      setIsLoading(true);
      setError('');
      // Load prompt_1 as default
      const response = await getSystemPromptSlot('prompt_1');
      if (response.status === 'Success') {
        const prompt = response.data.prompt || '';
        setSystemPrompt(prompt);
        setPromptSlots((prev) => ({ ...prev, prompt_1: prompt }));
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

  const loadAllPromptSlots = async () => {
    try {
      const slots = ['prompt_1', 'prompt_2', 'prompt_3'];
      const newPromptSlots = { ...promptSlots };

      for (const slot of slots) {
        try {
          const response = await getSystemPromptSlot(slot);
          if (response.status === 'Success') {
            newPromptSlots[slot as keyof PromptSlots] = response.data.prompt || '';
          }
        } catch (error) {
          console.log(`Error loading ${slot}:`, error);
          // Set empty string if there's an error loading
          newPromptSlots[slot as keyof PromptSlots] = '';
        }
      }

      setPromptSlots(newPromptSlots);
    } catch (error) {
      console.log('Error loading prompt slots:', error);
    }
  };

  const loadActivePromptSlot = async () => {
    try {
      const active = await getActiveSystemPromptSlot();
      setActiveSlot(active);
    } catch (error) {
      console.error('Error loading active prompt slot:', error);
    }
  };

  const handleSaveToSlot = async (slot: keyof PromptSlots) => {
    try {
      setIsSaving(true);
      setError('');
      console.log(`Saving to slot ${slot}:`, systemPrompt); // Add logging
      const response = await updateSystemPromptSlot(slot, systemPrompt);
      console.log('Save response:', response); // Add logging
      if (response.status === 'Success') {
        showSuccessToast(`Prompt saved to ${slot.replace('_', ' ')} successfully`);
        // Update local state
        setPromptSlots((prev) => ({ ...prev, [slot]: systemPrompt }));
      } else {
        setError(`Failed to save prompt to ${slot.replace('_', ' ')}`);
      }
    } catch (error) {
      console.error(`Error saving to ${slot}:`, error); // Better error logging
      setError(`Error saving prompt to ${slot.replace('_', ' ')}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoadFromSlot = async (slot: keyof PromptSlots) => {
    try {
      setIsLoading(true);
      setError('');
      const response = await getSystemPromptSlot(slot);
      if (response.status === 'Success') {
        const prompt = response.data.prompt || '';
        setSystemPrompt(prompt);
        setCurrentSlot(slot); // Set current slot
        // Update local state
        setPromptSlots((prev) => ({ ...prev, [slot]: prompt }));
        showSuccessToast(`Prompt loaded from ${slot.replace('_', ' ')}`);
      } else {
        setError(`Failed to load prompt from ${slot.replace('_', ' ')}`);
      }
    } catch (error) {
      setError(`Error loading prompt from ${slot.replace('_', ' ')}`);
      console.error(`Error loading prompt from ${slot}:`, error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSetActiveSlot = async (slot: keyof PromptSlots) => {
    try {
      setIsLoading(true);
      const success = await setActiveSystemPromptSlot(slot);
      if (success) {
        setActiveSlot(slot);
        // Show success message
        showSuccessToast(`Prompt ${getSlotDisplayName(slot)} is now active for graph building and interaction!`);
      }
    } catch (error) {
      console.error('Error setting active prompt slot:', error);
      showErrorToast('Failed to set active prompt slot');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setSystemPrompt('');
    setError('');
    onClose();
  };

  const getCurrentSlotDisplayName = () => {
    return getSlotDisplayName(currentSlot);
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
      <Dialog.Header className='flex-shrink-0'>
        <Typography variant='h4'>Edit System Prompt</Typography>
      </Dialog.Header>

      <Dialog.Content className='flex flex-col flex-1 min-h-0 p-4'>
        {error && <Banner type='danger' title='Error' description={error} className='mb-4 flex-shrink-0' />}

        {/* Active Prompt Indicator */}
        <Banner
          type='info'
          title={`Active Prompt: ${getSlotDisplayName(activeSlot)}`}
          description="This prompt is currently used for graph building and interaction. You can change it by clicking 'Set Active' on any prompt slot."
          className='mb-4 flex-shrink-0'
        />

        <div className='flex-1 flex flex-col min-h-0'>
          {/* Current Slot Indicator */}
          <div className='mb-2 p-2 bg-palette-neutral-bg-weak border border-palette-neutral-border-weak rounded text-sm'>
            <Typography variant='body-small' className='font-medium'>
              Currently Editing: {getCurrentSlotDisplayName()}
            </Typography>
          </div>
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
              minHeight: '80vh', // Increased from 60vh to 70vh
              resize: 'none',
              overflow: 'auto',
              height: '100%',
            }}
          />
          {isLoading && <div className='text-sm text-gray-500 mt-2 flex-shrink-0'>Loading system prompt...</div>}
          <div className='text-xs text-gray-400 mt-2 flex-shrink-0'>Character count: {systemPrompt.length}</div>
        </div>

        {/* Prompt Slot Management */}
        <div className='mt-4 p-4 border border-palette-neutral-border-weak rounded-lg bg-palette-neutral-bg-weak'>
          <Typography variant='body-medium' className='font-semibold mb-3'>
            Prompt Slots
          </Typography>
          <div className='grid grid-cols-3 gap-3'>
            {(['prompt_1', 'prompt_2', 'prompt_3'] as const).map((slot) => (
              <div key={slot} className='flex flex-col gap-2'>
                <div className='flex items-center justify-between'>
                  <Typography variant='body-small' className='font-medium'>
                    {getSlotDisplayName(slot)}
                  </Typography>
                  <div className='text-xs text-gray-500'>
                    {promptSlots[slot] ? `${promptSlots[slot].length} chars` : 'Empty'}
                  </div>
                </div>
                <div className='flex gap-2'>
                  <Button
                    fill='outlined'
                    size='small'
                    onClick={() => handleLoadFromSlot(slot)}
                    isDisabled={isLoading}
                    className='flex-1'
                  >
                    Load {slot.replace('prompt_', 'P')}
                  </Button>
                  <Button
                    fill='filled'
                    size='small'
                    onClick={() => handleSaveToSlot(slot)}
                    isDisabled={isSaving}
                    className='flex-1'
                  >
                    Save {slot.replace('prompt_', 'P')}
                  </Button>
                  <Button
                    fill='outlined'
                    size='small'
                    onClick={() => handleSetActiveSlot(slot)}
                    isDisabled={isLoading || activeSlot === slot}
                    className='flex-1'
                  >
                    {activeSlot === slot ? 'Active' : 'Set Active'}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Dialog.Content>

      <Dialog.Actions className='flex-shrink-0 p-4 border-t border-palette-neutral-border-weak'>
        <div className='flex gap-3 justify-end w-full'>
          <Button fill='text' onClick={handleCancel} isDisabled={isSaving} size='medium'>
            Cancel
          </Button>
        </div>
      </Dialog.Actions>
    </Dialog>
  );
};

export default SystemPromptEditor;
