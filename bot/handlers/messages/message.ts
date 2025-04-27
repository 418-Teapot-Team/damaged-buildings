import { Context, Keyboard } from "grammy";
import activeChats from "../../states/ActiveChats";
import { sendMessage } from "../../api/ai";
import { EndChatHandler } from "../commands";

export async function MessageHandler(ctx: Context) {
  const userID = ctx.from.id;
  try {
    if (activeChats.isChatActive(userID)) {
      const resp = await sendMessage(
        userID,
        ctx.message.text,
        activeChats.getChatAgent(userID)
      );

      const keyboard = new Keyboard().text("/end_chat").resized();

      ctx.reply(resp.message, { reply_markup: keyboard });
    }
  } catch (error) {
    console.log(error);
  }
}
