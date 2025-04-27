import { Context, Keyboard } from "grammy";
import activeChats from "../../states/ActiveChats";
import { getAgent } from "../../api/ai";

export async function StartChatHandler(ctx: Context) {
  try {
    const config = await getAgent(ctx.from.id);
    activeChats.startChat(ctx.from.id, config);
    const keyboard = new Keyboard().text("/end_chat").resized();
    ctx.reply("Chat started, feel free to ask :)", { reply_markup: keyboard });
  } catch (err) {
    console.log(err);
  }
}
