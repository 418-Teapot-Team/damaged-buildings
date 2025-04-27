import { Context } from "grammy";
import { buildHelpMessage } from "../../utils";

export function HelpHandler(ctx: Context) {
  ctx.reply(buildHelpMessage());
}
