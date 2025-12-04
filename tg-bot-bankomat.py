from telegram  import (Update, 
                        ReplyKeyboardMarkup, 
                        ReplyKeyboardRemove,
                        )
from telegram.ext import ( ApplicationBuilder,
                            CommandHandler,
                            ContextTypes,
                            MessageHandler,
                            filters,
                            ConversationHandler
                            )
import random as r
import dotenv
import os
dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")


class Registration:
    CARD_ENTER, PIN_CODE = range(2)
    def __init__(self):
        self.handler = ConversationHandler(
            entry_points=[CommandHandler("auth", self.start_auth)],
            states={
                self.CARD_ENTER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.enter_card_number)
                ],
                self.PIN_CODE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.enter_pin_code)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        self.base_data = base_data
        self.user_card_number = ""
        self.pin_code = ""
    
    async def start_auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("is_authorized"):
            await update.message.reply_text("Вы уже авторизованы.")
            return ConversationHandler.END

        await update.message.reply_text("Вставьте вашу карту (введите номер карты):")
        return self.CARD_ENTER

    async def enter_card_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        if user_text in self.base_data:
            self.user_card_number = user_text
            if base_data[self.user_card_number]["ban"]:
                await update.message.reply_text("Аккаунт заблокирован")
                return ConversationHandler.END
            await update.message.reply_text("Введите PIN-код:")
            return self.PIN_CODE
        else:
            await update.message.reply_text("Вы ввели неверный номер карты, попробуйте снова:")
            return self.CARD_ENTER

    async def enter_pin_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        user = update.message.from_user
        username = user.username
        if user_text == self.base_data[self.user_card_number]["pin"]:
            context.user_data["is_authorized"] = True
            context.user_data["card_number"] = self.user_card_number
            users.append(username)
            menu = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Авторизация прошла успешно!",
                reply_markup=menu
            )
            
            return ConversationHandler.END
        else:
            await update.message.reply_text("Неверный PIN-код, попробуйте снова:")
            return self.PIN_CODE

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Авторизация отменена.")
        return ConversationHandler.END
    
def check_block(func):
    async def wrapper(self, update:Update, context: ContextTypes):
        if context.user_data.get("is_authorized") != True:
            await update.message.reply_text("Вы не прошли регистрацию. Пройдите регистрацию по команде /auth")
            return ConversationHandler.END
        if base_data[context.user_data["card_number"]]["ban"]:
            await update.message.reply_text("Аккаунт заблокирован")
            return ConversationHandler.END
        return await func(self, update, context)
    return wrapper

def check_admin(func):
    async def wrapper(self, update:Update, context: ContextTypes):
        if context.user_data["card_number"] != "":
            if not base_data[context.user_data["card_number"]]["admin"]:
                return await update.message.reply_text("У Вас нет прав администратора для использования этой команды") 
            return await func(self, update, context)
        else:
            return await update.message.reply_text("Пройдите регистрацию /auth") 
    return wrapper



    

class Commands:
    def __init__(self, app):

        start_handler = CommandHandler("start",self.start)
        app.add_handler(start_handler)

        help_handler = CommandHandler("help",self.help)
        app.add_handler(help_handler)

        admin_handler = CommandHandler("admin",self.admin_panel)
        app.add_handler(admin_handler)

        history_handler = CommandHandler("history",self.show_history)
        app.add_handler(history_handler)
        
        users_handler = CommandHandler("users", self.show_users)
        app.add_handler(users_handler)

        logs_handler = CommandHandler("logs", self.show_logs)
        app.add_handler(logs_handler)

        block_handler = CommandHandler("block", self.block_card)
        app.add_handler(block_handler)

        unblock_handler = CommandHandler("unblock", self.unblock_card)
        app.add_handler(unblock_handler)

        registration_conv = Registration()
        app.add_handler(registration_conv.handler)


    async def start(self,update:Update, context: ContextTypes):
        context.user_data["card_number"] = "" 
        await update.message.reply_text("Привет! Добро пожаловать в Банкомат-бот!")

    async def help(self, update:Update, context: ContextTypes):
        await update.message.reply_text('''Вот, что я умею:
/start - приветствие
/auth - авторизация
/history - история операций
/help - показать это сообщение''')
        
    @check_admin
    async def admin_panel(self, update:Update, context: ContextTypes):
        await update.message.reply_text('''Команды админа:
/logs - показать логи
/users - показать пользователей
/block <номер карты> - заблокировать карту
/unblock <номер карты> - разблокировать карту''')

    @check_block
    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "История операций:\n"
        for operation in base_data[context.user_data["card_number"]]["history"]:
            text += f"{operation}\n"
        await update.message.reply_text(text.strip())

    @check_admin
    async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "Пользователи:\n"
        for user in users:
            text += f"{user}\n"
        await update.message.reply_text(text.strip())

    @check_admin
    async def show_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "Логи:\n"
        for log in logs:
            text += f"{log}\n"
        await update.message.reply_text(text.strip())
    
    @check_admin
    async def block_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.split()
        try:
            card_number = text[1]
        except:
            return await update.message.reply_text(f"Вы не ввели номер карты")
        if card_number in base_data:
            if base_data[card_number]["ban"] == False:
                base_data[card_number]["ban"] = True
                await update.message.reply_text(f"Карта {card_number} заблокирована")
                logs.append(f"Блокировка карты {card_number}")
            else:
                await update.message.reply_text(f"Карта {card_number} уже заблокирована")
        else:
            await update.message.reply_text(f"Карты {card_number} нет в базе данных")

    @check_admin
    async def unblock_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.split()
        try:
            card_number = text[1]
        except:
            return await update.message.reply_text(f"Вы не ввели номер карты")
        if card_number in base_data:
            if base_data[card_number]["ban"] == True:
                base_data[card_number]["ban"] = False
                await update.message.reply_text(f"Карта {card_number} разблокирована")
                logs.append(f"Разблокировка карты {card_number}")
            else:
                await update.message.reply_text(f"Карта {card_number} уже разблокирована")
        else:
            await update.message.reply_text(f"Карты {card_number} нет в базе данных")

    

class Withdraw:
    AMOUNT_ENTER, CONFIRM, CONFIRM_CODE = range(3)
    def __init__(self):
        self.handler = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & filters.Regex("Снять деньги"), self.start_withdraw)],
            states={
                self.AMOUNT_ENTER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.withdraw)
                ],
                self.CONFIRM: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm_code)
                ],
                self.CONFIRM_CODE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        self.amount = 0
        self.confirm_code_enter = ""

    @check_block
    async def start_withdraw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Введите сумму для снятия:",
        reply_markup=ReplyKeyboardRemove() 
        )
        return self.AMOUNT_ENTER
            
    async def withdraw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        
        if user_text.isdigit() == True:
            self.amount = int(user_text)
            await update.message.reply_text(f"Подтвердите снятие {self.amount}₽:",
            reply_markup=ReplyKeyboardMarkup(confirm_keyboard, resize_keyboard=True)
            )
            return self.CONFIRM
        
        else:
            await update.message.reply_text("Вы ввели неверную сумму, попробуйте снова:")
            return self.AMOUNT_ENTER
        
    async def confirm_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        self.confirm_code_enter = ""
        if user_text == "Да":
            for i in range(4):
                self.confirm_code_enter += str(r.randint(0,9))
            await update.message.reply_text(f"Введите код для продолжения операции ({self.confirm_code_enter})",
            reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True))
            return self.CONFIRM
        elif user_text == "Нет":
            await update.message.reply_text("Снятие средств отменено",
            reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text("Некорректный ввод. Поробуйте снова",
            )
            return self.CONFIRM_CODE
    
    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        if user_text == self.confirm_code_enter:
            card_number = context.user_data["card_number"]
            if base_data[card_number]["balance"] >= self.amount:
                base_data[card_number]["balance"] -= self.amount

                base_data[card_number]["history"].append(f"Снятие: -{self.amount}₽")
                logs.append(f"Снятие {card_number} -{self.amount}₽")

                await update.message.reply_text(f"Вы сняли {self.amount}₽", 
                reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
            )
                return ConversationHandler.END
            else:
                await update.message.reply_text("На вашем счету недостаточно средств.", 
                reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
            )
                return ConversationHandler.END
        else:
            await update.message.reply_text("Некорректный ввод. Поробуйте снова",
            )
            return self.CONFIRM
        
        
        
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Снятие средств отменено",
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
        )
        return ConversationHandler.END

            
            

class Deposit:
    CARD_ENTER, CONFIRM, CONFIRM_CODE, DEPOSIT = range(4)
    def __init__(self):
        self.handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("Пополнить счёт"), self.start_deposit)],
        states={
            self.CARD_ENTER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.enter_card_number)
            ],
            self.CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm)
            ],
            self.CONFIRM_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm_code)
            ],
            self.DEPOSIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.deposit)
            ]
        },
        fallbacks=[CommandHandler("cancel", self.cancel)],
    )
        
        self.card_number = ""
        self.confirm_code_enter = ""
        self.amount = 0
    
    @check_block
    async def start_deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Введите номер карты:",
        reply_markup=ReplyKeyboardRemove() 
        )
        
        return self.CARD_ENTER
        
    async def enter_card_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        
        if user_text in base_data:
            self.card_number = user_text
            await update.message.reply_text("Введите сумму для пополнения: ",
            reply_markup=ReplyKeyboardRemove()
            )
            return self.CONFIRM
        else:
            await update.message.reply_text("Вы ввели неверный номер карты, попробуйте снова:")
            return self.CARD_ENTER
        

    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        if user_text.isdigit():
            if base_data[user_text]["ban"] == True:
                await update.message.reply_text(f"Cчет *****{self.card_number[5:]} заблокирован")
            self.amount = int(user_text)
            await update.message.reply_text(f"Подтвердите перевод на счет *****{self.card_number[5:]} на {self.amount}₽",
            reply_markup=ReplyKeyboardMarkup(confirm_keyboard, resize_keyboard=True)
            )
            return self.CONFIRM_CODE
        
        else:
            await update.message.reply_text("Вы ввели неверную сумму, попробуйте снова:")
            return self.CONFIRM
        
    async def confirm_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        self.confirm_code_enter = ""
        if user_text == "Да":
            for i in range(4):
                self.confirm_code_enter += str(r.randint(0,9))
            await update.message.reply_text(f"Введите код для продолжения операции ({self.confirm_code_enter})",
            reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True))
            return self.DEPOSIT
        elif user_text == "Нет":
            await update.message.reply_text("Перевод средств отменен.",
            reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text("Некорректный ввод. Поробуйте снова",
            )
            return self.CONFIRM_CODE
    
    async def deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        if user_text == self.confirm_code_enter:
            if base_data[context.user_data["card_number"]]["balance"] >= self.amount:
                base_data[self.card_number]["balance"] += self.amount #пополнение на карту
                base_data[context.user_data["card_number"]]["balance"] -= self.amount #снятие средств со счёта пользователя

                base_data[context.user_data["card_number"]]["history"].append(f"Перевод -{self.amount}₽ на счет *****{self.card_number[5:]}")
                

                base_data[self.card_number]["history"].append(f"Пополнение +{self.amount}₽")
                logs.append(f"Пополнение {self.card_number} +{self.amount}₽")

                await update.message.reply_text(f"Операция успешна. Остаток: {base_data[context.user_data['card_number']]['balance']}₽",
                reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
                )
                return ConversationHandler.END
            else:
                await update.message.reply_text("На вашем счету недостаточно средств.",
                reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
                )
                return ConversationHandler.END
        else:
            await update.message.reply_text("Некорректный ввод. Поробуйте снова",
            reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
            )
            return self.DEPOSIT
        
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Пополнение средств отменено",
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
        )
        return ConversationHandler.END
            

class Text_Handler:
    def __init__(self, app):
            withdraw_conv = Withdraw()
            app.add_handler(withdraw_conv.handler)

            deposit_conv = Deposit()
            app.add_handler(deposit_conv.handler)

            text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self)
            app.add_handler(text_handler)

            self.all_user_text = []

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text

        actions = {
            "Проверить баланс": self.show_balance,
            "Выйти": self.logout,
        }

        action = actions.get(user_text)
        if action:
            await action(update, context)
        else:
            await update.message.reply_text("Чтобы узнать, что я умею, напишите /help")

    @check_block
    async def show_balance(self, update, context):
        await update.message.reply_text(f"Ваш текущий баланс: {base_data[context.user_data['card_number']]['balance']}₽")

    async def logout(self, update, context):
        context.user_data["is_authorized"] = False
        context.user_data["card_number"] = ""
        await update.message.reply_text("Вы вышли из системы.",
        reply_markup=ReplyKeyboardRemove() 
        )

def main():
    builder_app = ApplicationBuilder()#Создаем конфигуратор приложения
    builder_app.token(token=TOKEN)

    app = builder_app.build()#Функция создает бота (ядро приложения)

    global base_data, logs, users, menu_keyboard, confirm_keyboard
    base_data = {
    "123456789": {
                "pin": "4321", 
                "balance": 203004, 
                "history": [],
                "ban": False,
                "admin": True
                }, 
    "987654321": {
                "pin": "1234", 
                "balance": 50, 
                "history": [],
                "ban": False, 
                "admin": False
                }
    }
    users = []
    logs = []
    menu_keyboard = [
        ["Проверить баланс", "Пополнить счёт"],
        ["Снять деньги", "Выйти"]
    ]

    confirm_keyboard = [
        ["Да", "Нет"]
    ]
    

    commands = Commands(app)
    text_handler = Text_Handler(app)


    

    print("Бот запущен...")
    app.run_polling()#Начинаем опрашивать телеграмм

main()
