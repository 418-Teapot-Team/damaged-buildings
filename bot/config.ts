import "dotenv/config";

class Config {
  private envs: any = {};
  constructor() {
    this.envs.BOT_TOKEN = process.env.BOT_TOKEN || "";
    this.envs.API_URL = process.env.API_URL || "";
  }
  public valueOf(key: string) {
    return this.envs[key];
  }
}

export default new Config();
