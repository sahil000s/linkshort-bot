from telegram.ext import Updater, CommandHandler
from github import Github
import os, json, random, string, base64

TG_TOKEN = os.environ['TELEGRAM_TOKEN']
GH_TOKEN = os.environ['GITHUB_TOKEN']
REPO_NAME = "username/shortener-repo"
FILE_PATH = "links.json"

gh = Github(GH_TOKEN)
repo = gh.get_repo(REPO_NAME)

def get_links():
    file = repo.get_contents(FILE_PATH)
    data = json.loads(base64.b64decode(file.content).decode())
    return data, file

def save_links(data, file, msg):
    repo.update_file(FILE_PATH, msg, json.dumps(data, indent=2), file.sha)

def random_code(length=6):
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def short(update, context):
    if len(context.args) < 2:
        update.message.reply_text("Usage: /short <APK_URL> <APK_NAME>")
        return
    url = context.args[0]
    name = " ".join(context.args[1:])
    data, file = get_links()
    code = random_code()
    while code in data:
        code = random_code()
    data[code] = {"url": url, "name": name}
    save_links(data, file, f"Add {name} ({code})")
    update.message.reply_text(f"✅ Short link created:\nhttps://username.github.io/{code}\n({name})")

def list_links(update, context):
    data, _ = get_links()
    if not data:
        update.message.reply_text("No links found.")
        return
    text = "📂 Stored Links:\n"
    for i,(code,info) in enumerate(data.items(), start=1):
        text += f"{i}. {code} → {info['name']}\n"
    update.message.reply_text(text)

def view(update, context):
    if not context.args:
        update.message.reply_text("Usage: /view <code>")
        return
    code = context.args[0]
    data, _ = get_links()
    if code not in data:
        update.message.reply_text("❌ Code not found.")
        return
    info = data[code]
    update.message.reply_text(
        f"🔗 Code: {code}\n📱 APK: {info['name']}\n📥 URL: {info['url']}"
    )

def edit(update, context):
    if len(context.args) < 3:
        update.message.reply_text("Usage: /edit <code> <new-url> <new-name>")
        return
    code = context.args[0]
    new_url = context.args[1]
    new_name = " ".join(context.args[2:])
    data, file = get_links()
    if code not in data:
        update.message.reply_text("❌ Code not found.")
        return
    data[code] = {"url": new_url, "name": new_name}
    save_links(data, file, f"Edit {code}")
    update.message.reply_text(f"✅ Updated {code}\nNew Name: {new_name}\nNew URL: {new_url}")

def delete(update, context):
    if not context.args:
        update.message.reply_text("Usage: /delete <code>")
        return
    code = context.args[0]
    data, file = get_links()
    if code not in data:
        update.message.reply_text("❌ Code not found.")
        return
    name = data[code]['name']
    del data[code]
    save_links(data, file, f"Delete {code}")
    update.message.reply_text(f"🗑 Deleted short link: {code} ({name})")

def main():
    updater = Updater(TG_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("short", short))
    dp.add_handler(CommandHandler("list", list_links))
    dp.add_handler(CommandHandler("view", view))
    dp.add_handler(CommandHandler("edit", edit))
    dp.add_handler(CommandHandler("delete", delete))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
