import { Context, Keyboard } from "grammy";
import activeChats from "../../states/ActiveChats";

export function EndChatHandler(ctx: Context) {
  activeChats.endChat(ctx.from.id);
  const keyboard = new Keyboard().text("/start_chat").resized();
  ctx.reply("Chat finished, thank you for using our bot!", {
    reply_markup: keyboard,
  });
}
