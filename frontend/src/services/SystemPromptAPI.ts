import api from '../API/Index';

export const getSystemPrompt = async () => {
  try {
    const response = await api.get('/system_prompt');
    console.log('System prompt:', response.data);
    return response.data;
  } catch (error) {
    console.log('Error getting system prompt:', error);
    throw error;
  }
};

export const updateSystemPrompt = async (systemPrompt: string) => {
  try {
    const formData = new FormData();
    formData.append('system_prompt', systemPrompt);
    const response = await api.post('/update_system_prompt', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.log('Error updating system prompt:', error);
    throw error;
  }
}; 