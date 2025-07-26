import { createContext, Dispatch, SetStateAction } from "react";

export type InteractionMode = "conversational" | "informational";

export type ConversationType = "voice-to-voice" | "text-voice" | null;

export interface ScenarioConfig {
  language: string;
  scenario_title: string;
  scenario: string;
  level: string;
  metrics?: Array<{
    metric: string;
    description: string;
    min_score: number;
    max_score: number;
  }>;
}

interface AppStateContextValue {
  conversationId: string;
  setConversationId: Dispatch<SetStateAction<string>>;
  conversationType: ConversationType;
  setConversationType: Dispatch<SetStateAction<ConversationType>>;
  interactionMode: InteractionMode;
  setInteractionMode: Dispatch<SetStateAction<InteractionMode>>;
  searchQuery: string;
  setSearchQuery: Dispatch<SetStateAction<string>>;
  scenarioConfig: ScenarioConfig | null;
  setScenarioConfig: Dispatch<SetStateAction<ScenarioConfig | null>>;
  geminiApiKey: string;
  webrtcEnabled: boolean;
  websocketEnabled: boolean;
}

const noop = () => {};

export const AppStateContext = createContext<AppStateContextValue>({
  conversationId: "",
  setConversationId: noop,
  conversationType: null,
  setConversationType: noop,
  interactionMode: "informational",
  setInteractionMode: noop,
  searchQuery: "",
  setSearchQuery: noop,
  scenarioConfig: null,
  setScenarioConfig: noop,
  geminiApiKey: "",
  webrtcEnabled: false,
  websocketEnabled: false,
});
