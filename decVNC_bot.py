import subprocess
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

# Настройка логирования
log_file_path = '/var/log/TGbot/decVNC.log'

# Убедитесь, что у вас есть права на запись в указанный файл и каталог
logging.basicConfig(filename=log_file_path,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция, которая выполняет команду и возвращает результат
def run_command(value):
    try:
        command = f"echo -n {value} | xxd -r -p | openssl enc -des-cbc --nopad --nosalt -K e84ad660c4721ae0 -iv 0000000000000000 -d | hexdump -Cv | grep -oP '\|\K[^|]+'| sed 's/\.//g'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return str(e)

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} started the bot.")
    update.message.reply_text("Привет! Отправь мне значение, и я выполню decrypt vnc password.")

# Обработчик текстовых сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text
    logger.info(f"User {user_id} sent message:\n{user_input}")

    # Разделяем сообщение на строки
    lines = user_input.split('\n')
    results = []

    for line in lines:
        result = run_command(line.strip())
        if not result:
            result = "Команда вернула пустой результат или произошла ошибка."
        results.append(result)
        logger.info(f"Processed line: {line.strip()}")
        logger.info(f"Bot replied to user {user_id} with: {result}")

    # Объединяем результаты в одну строку для ответа
    response = '\n'.join(results)
    update.message.reply_text(response)

def main():
    # Вставьте сюда ваш токен бота
    TOKEN = 'TOKEN'

    # Создаем updater и dispatcher
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Добавляем обработчики команд и сообщений
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
