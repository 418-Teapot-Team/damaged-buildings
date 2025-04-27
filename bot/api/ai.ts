import axios from "axios";
import config from "../config";

export type AgentConfig = {
  configurable: {
    thread_id: string;
  };
};

const API_URL = config.valueOf("API_URL");

export async function getAgent(userID: number): Promise<AgentConfig> {
  const res = await axios.post(`${API_URL}/get-agent`, {
    user_id: userID,
  });
  return res.data.message;
}

export async function sendMessage(
  userID: number,
  message: string,
  config: AgentConfig
) {
  const res = await axios.post(`${API_URL}/answer-question`, {
    user_id: userID,
    user_message: message,
    config: config,
  });

  return res.data;
}
