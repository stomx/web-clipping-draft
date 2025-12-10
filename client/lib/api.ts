export const API_URL = "http://localhost:8000";

export interface ResearchRequest {
  query: string;
  lang?: string;
  format?: string;
  start_date?: string;
  end_date?: string;
  start_time?: string;
  end_time?: string;
  count?: number;
  mode?: "stream" | "async";
}

export interface ResearchEvent {
    type: string;
    data: any;
}

export async function startResearch(data: ResearchRequest) {
  const response = await fetch(`${API_URL}/research`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Error: ${response.statusText}`);
  }

  return response;
}

export async function* streamResearch(data: ResearchRequest): AsyncGenerator<any, void, unknown> {
    const response = await startResearch({...data, mode: 'stream'});
    
    if (!response.body) return;

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || ''; // Keep incomplete part

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const content = line.slice(6);
                    if (content === '[DONE]') return;
                    try {
                        yield JSON.parse(content);
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    } finally {
        reader.releaseLock();
    }
}
