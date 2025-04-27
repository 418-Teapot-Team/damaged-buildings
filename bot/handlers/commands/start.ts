import { Context, Keyboard } from "grammy";
import { buildHelpMessage } from "../../utils";

export function StartHandler(ctx: Context) {
  const greeting = `👋 Welcome to the Building Damage Evaluation Bot!\n\nThis bot helps you evaluate and report damaged buildings. You can provide photos and descriptions, and we'll help assess the damage level.\n\nWould you like to begin?\n\n\n${buildHelpMessage()}`;

  const keyboard = new Keyboard().text("/start_chat").resized();

  ctx.reply(greeting, { reply_markup: keyboard });
}
