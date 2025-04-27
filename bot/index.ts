import { Bot } from "grammy";
import config from "./config";
import {
  EndChatHandler,
  HelpHandler,
  StartChatHandler,
  StartHandler,
} from "./handlers/commands";
import { MessageHandler } from "./handlers/messages/message";

const bot = new Bot(config.valueOf("BOT_TOKEN"));

bot.command("start", StartHandler);
bot.command("help", HelpHandler);
bot.command("start_chat", StartChatHandler);
bot.command("end_chat", EndChatHandler);
bot.on("message", MessageHandler);

bot.start();
