export interface ScenarioMetric {
    metric: string;
    description: string;
    min_score: number;
    max_score: number;
  }
  
  export interface ScenarioResponse {
    scenario: string;
    metrics: ScenarioMetric[];
  }
  
  export interface ScenarioRequest {
    level: string;
    topic: string;
    other_instructions: string;
  }
  
  export async function createScenario(data: ScenarioRequest): Promise<ScenarioResponse> {
  try {
    const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/scenarios`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to create scenario');
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating scenario:', error);
    throw error;
  }
} 