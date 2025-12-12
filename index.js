const TelegramBot = require("node-telegram-bot-api");

// ENV VARIABLES (SET THESE IN KOYEB)
const BOT_TOKEN = process.env.BOT_TOKEN;

// ADD CHAT IDS OF YOUR LOVED ONES
const RECIPIENTS = process.env.RECIPIENTS
  .split(",")
  .map(id => Number(id));

const bot = new TelegramBot(BOT_TOKEN, { polling: true });

console.log("Bot is running...");

// Forward audio & video messages
bot.on("message", (msg) => {
  if (!RECIPIENTS.includes(msg.chat.id)) return;

  for (const id of RECIPIENTS) {
    if (msg.voice) {
      bot.sendVoice(id, msg.voice.file_id);
    }

    if (msg.audio) {
      bot.sendAudio(id, msg.audio.file_id);
    }

    if (msg.video) {
      bot.sendVideo(id, msg.video.file_id);
    }

    if (msg.video_note) {
      bot.sendVideoNote(id, msg.video_note.file_id);
    }
  }
});
