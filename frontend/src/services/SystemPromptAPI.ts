import api from '../API/Index';

// New functions for multiple prompt slots
export const getSystemPromptSlot = async (slot: string) => {
  try {
    const response = await api.get(`/get_system_prompt_slot/${slot}`);
    console.log(`System prompt ${slot}:`, response.data);
    return response.data;
  } catch (error) {
    console.log(`Error getting system prompt ${slot}:`, error);
    throw error;
  }
};

export const updateSystemPromptSlot = async (slot: string, prompt: string) => {
  try {
    const formData = new FormData();
    formData.append('slot', slot);
    formData.append('prompt', prompt);
    const response = await api.post('/update_system_prompt_slot', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.log(`Error updating system prompt ${slot}:`, error);
    throw error;
  }
};

export const getActiveSystemPromptSlot = async (): Promise<string> => {
  try {
    const response = await api.get('/get_active_system_prompt_slot');
    if (response.data.status === 'Success') {
      return response.data.data.active_slot;
    }
    throw new Error(response.data.message || 'Failed to get active prompt slot');
  } catch (error) {
    console.error('Error getting active prompt slot:', error);
    throw error;
  }
};

export const setActiveSystemPromptSlot = async (slot: string): Promise<boolean> => {
  try {
    const formData = new FormData();
    formData.append('slot', slot);

    const response = await api.post('/set_active_system_prompt_slot', formData);
    if (response.data.status === 'Success') {
      // Refresh the cache after setting the active prompt
      await refreshSystemPromptCache();
      return true;
    }
    throw new Error(response.data.message || 'Failed to set active prompt slot');
  } catch (error) {
    console.error('Error setting active prompt slot:', error);
    throw error;
  }
};

export const refreshSystemPromptCache = async (): Promise<boolean> => {
  try {
    const response = await api.post('/refresh_system_prompt_cache');
    if (response.data.status === 'Success') {
      console.log('System prompt cache refreshed successfully');
      return true;
    }
    throw new Error(response.data.message || 'Failed to refresh system prompt cache');
  } catch (error) {
    console.error('Error refreshing system prompt cache:', error);
    throw error;
  }
};
