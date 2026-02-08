const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  
  return response.json();
}

export async function getDocumentStatus(documentId: string) {
  const response = await fetch(`${API_URL}/api/documents/${documentId}`);
  if (!response.ok) return null;
  return response.json();
}

export async function listDocuments() {
  const response = await fetch(`${API_URL}/api/documents`);
  if (!response.ok) return [];
  return response.json();
}

export async function deleteDocument(documentId: string) {
  const response = await fetch(`${API_URL}/api/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Delete failed');
  }
  return response.json();
}

export async function listConversations() {
  const response = await fetch(`${API_URL}/api/conversations`);
  if (!response.ok) return [];
  return response.json();
}

export async function getConversationMessages(conversationId: string) {
  const response = await fetch(`${API_URL}/api/conversations/${conversationId}/messages`);
  if (!response.ok) return [];
  return response.json();
}

export async function deleteConversation(conversationId: string) {
  const response = await fetch(`${API_URL}/api/conversations/${conversationId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Delete failed');
  return response.json();
}

export async function chat(question: string, documentIds?: string[], conversationId?: string) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      document_ids: documentIds,
      conversation_id: conversationId,
    }),
  });
  
  return response;
}

export async function exportConversation(conversationId: string) {
  const response = await fetch(`${API_URL}/api/conversations/${conversationId}/export`);
  if (!response.ok) throw new Error('Export failed');
  return response.json();
}

export async function renameConversation(conversationId: string, title: string) {
  const response = await fetch(`${API_URL}/api/conversations/${conversationId}/rename`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) throw new Error('Rename failed');
  return response.json();
}
